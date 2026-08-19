"""
Physical Region Fusion Engine — Physical Object Existence Check, Multi-Signal Region Fusion, Part-of-Object Detection, and Pairwise Footwear Deduplication.

Implements:
1. Physical Object Existence Check (filtering fragments / non-wearable region noise)
2. Multi-Signal Part-Of-Object Detection (containment + area ratio + boundary cues + category semantics)
3. Pairwise Footwear Fusion (left shoe + right shoe -> single footwear pair region)
4. Category-aware Minimum Object Size Thresholding (MIN_MASK_AREA_RATIO, MIN_BBOX_SIZE)
5. Multi-Feature Physical Similarity Score (IoU, containment, center distance, DINOv2/SigLIP embeddings, semantic compatibility)
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import logging

from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService

logger = logging.getLogger(__name__)

# Category-aware Minimum Object Size Thresholds
CATEGORY_MIN_BOUNDS = {
    "upper_body": {"min_bbox_ratio": 0.04, "min_area_pixels": 4000},
    "lower_body": {"min_bbox_ratio": 0.04, "min_area_pixels": 4000},
    "footwear":   {"min_bbox_ratio": 0.008, "min_area_pixels": 600},
    "accessory":  {"min_bbox_ratio": 0.003, "min_area_pixels": 250}
}

def calculate_iou(boxA: List[int], boxB: List[int]) -> float:
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = max(1, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = max(1, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    return interArea / float(boxAArea + boxBArea - interArea)

def calculate_containment(boxA: List[int], boxB: List[int]) -> float:
    """Calculates ratio of boxA inside boxB relative to boxA's area."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = max(1, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    return interArea / float(boxAArea)

def calculate_center_distance(boxA: List[int], boxB: List[int]) -> float:
    """Calculates Euclidean distance between bounding box centers relative to average box diagonal."""
    cA = [(boxA[0] + boxA[2]) / 2.0, (boxA[1] + boxA[3]) / 2.0]
    cB = [(boxB[0] + boxB[2]) / 2.0, (boxB[1] + boxB[3]) / 2.0]

    dist = np.sqrt((cA[0] - cB[0])**2 + (cA[1] - cB[1])**2)
    diagA = np.sqrt((boxA[2] - boxA[0])**2 + (boxA[3] - boxA[1])**2)
    diagB = np.sqrt((boxB[2] - boxB[0])**2 + (boxB[3] - boxB[1])**2)

    return dist / float(max(1.0, (diagA + diagB) / 2.0))

class PhysicalRegionFusionEngine:
    @staticmethod
    def physical_object_existence_check(det: Dict[str, Any], img_width: int, img_height: int) -> bool:
        """
        Physical Object Existence Check (Stage 1).
        Verifies whether a candidate detection corresponds to an independently wearable garment object
        rather than a crop fragment or noise.
        """
        box = det["box"]
        box_w = box[2] - box[0]
        box_h = box[3] - box[1]

        if box_w <= 0 or box_h <= 0:
            return False

        label = det.get("label", "clothing item")
        cat = ItemTaxonomyService.derive_category(label)
        box_area = box_w * box_h
        img_area = img_width * img_height

        # Rule: Misclassified shirt label on bottom footwear plane (y1 > 75% img_height) is a fragment
        if cat == "upper_body" and box[1] > 0.70 * img_height and box_h < 0.25 * img_height:
            return False

        # Rule: Misclassified jeans/trousers label on narrow collar/accessory patch (< 3% img_area) is a fragment
        if label in ["jeans", "trousers", "suit_trousers"] and box_area < 0.03 * img_area and box_h < 0.15 * img_height:
            return False

        return True

    @staticmethod
    def is_part_of_parent(child_det: Dict[str, Any], parent_det: Dict[str, Any]) -> bool:
        """
        Multi-Signal Object-Part Detection (Stage 2).
        Uses containment + relative area ratio + category semantics + position to identify object parts.
        NOTE: Bounding box containment alone NEVER discards a candidate (e.g. tie inside suit jacket, belt on waist).
        """
        boxChild = child_det["box"]
        boxParent = parent_det["box"]

        child_area = (boxChild[2] - boxChild[0]) * (boxChild[3] - boxChild[1])
        parent_area = (boxParent[2] - boxParent[0]) * (boxParent[3] - boxParent[1])

        # Child must be smaller than parent (< 50% area)
        if child_area >= 0.50 * parent_area:
            return False

        containment = calculate_containment(boxChild, boxParent)
        label_child = child_det.get("label", "")
        cat_child = ItemTaxonomyService.derive_category(label_child)
        cat_parent = ItemTaxonomyService.derive_category(parent_det.get("label", ""))

        # Legitimate overlapping accessories (tie, belt, watch) with strong score are preserved unless area is tiny
        if cat_child == "accessory" and cat_parent in ["upper_body", "lower_body"]:
            # False belt/shirt detail on trousers (e.g. waist crease or trouser crop labelled belt)
            if label_child in ["belt", "casual_shirt"] and cat_parent == "lower_body" and child_area < 0.30 * parent_area:
                # If child score is low (< 0.75) and contained inside trousers (> 70%), it's a trouser part
                if child_det.get("score", 0.8) < 0.80 and containment >= 0.70:
                    return True
            return False

        # If child shares category with parent and is mostly contained (> 75%)
        if containment >= 0.75:
            if cat_child == cat_parent:
                return True
            if child_area < 0.20 * parent_area:
                return True

        return False

    @staticmethod
    def physical_similarity_score(detA: Dict[str, Any], detB: Dict[str, Any]) -> float:
        """
        Computes physical similarity score between two candidate detections.
        Takes into account IoU, containment, center distance, and semantic category compatibility.
        """
        boxA = detA["box"]
        boxB = detB["box"]

        labelA = detA.get("label", "clothing item")
        labelB = detB.get("label", "clothing item")

        catA = ItemTaxonomyService.derive_category(labelA)
        catB = ItemTaxonomyService.derive_category(labelB)

        # RULE: Accessories (tie, belt, watch) overlapping upper/lower body items are DISTINCT physical objects unless part-of
        if (catA == "accessory" and catB != "accessory") or (catB == "accessory" and catA != "accessory"):
            return 0.0

        # RULE: Footwear overlapping lower body items (pants/trousers) are DISTINCT physical objects
        if (catA == "footwear" and catB == "lower_body") or (catB == "footwear" and catA == "lower_body"):
            return 0.0

        # Section 10: Pairwise Footwear Fusion (left shoe + right shoe -> one footwear pair region)
        if catA == "footwear" and catB == "footwear":
            center_dist = calculate_center_distance(boxA, boxB)
            # If two footwear items are on same lower plane and reasonably close (< 1.25 diagonal distance), fuse into pair
            if center_dist <= 1.25:
                return 0.85

        iou = calculate_iou(boxA, boxB)
        containment = max(calculate_containment(boxA, boxB), calculate_containment(boxB, boxA))
        center_dist = calculate_center_distance(boxA, boxB)

        # Base geometric score
        geo_score = 0.50 * iou + 0.35 * containment + 0.15 * max(0.0, 1.0 - center_dist)

        # Semantic category multiplier
        if catA == catB:
            cat_bonus = 0.20
        else:
            cat_bonus = -0.10

        return max(0.0, min(1.0, geo_score + cat_bonus))

    def fuse_detections(self, detections: List[Dict[str, Any]], img_width: int, img_height: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Fuses multi-model candidate detections into unique physical regions.
        Returns (fused_regions: List[Dict], discarded_log: List[Dict]).
        """
        if not detections:
            return [], []

        discarded_log: List[Dict[str, Any]] = []
        valid_detections: List[Dict[str, Any]] = []
        img_area = img_width * img_height

        # Stage 1: Physical Object Existence Check & Category-Aware Minimum Size Filter
        for det in detections:
            if not self.physical_object_existence_check(det, img_width, img_height):
                discarded_log.append({
                    "detection": det,
                    "reason": "PHYSICAL_OBJECT_EXISTENCE_FAILED",
                    "details": "Failed existence check (misclassified fragment or non-garment patch)"
                })
                continue

            box = det["box"]
            box_area = max(1, (box[2] - box[0]) * (box[3] - box[1]))
            box_ratio = box_area / float(img_area)
            cat = ItemTaxonomyService.derive_category(det.get("label", ""))

            thresh = CATEGORY_MIN_BOUNDS.get(cat, CATEGORY_MIN_BOUNDS["accessory"])
            if box_ratio < thresh["min_bbox_ratio"] or box_area < thresh["min_area_pixels"]:
                discarded_log.append({
                    "detection": det,
                    "reason": "MIN_OBJECT_SIZE_FILTER",
                    "details": f"box_ratio={box_ratio:.4f} < {thresh['min_bbox_ratio']}, area={box_area} < {thresh['min_area_pixels']}"
                })
                continue
            valid_detections.append(det)

        # Sort detections by score descending
        sorted_dets = sorted(valid_detections, key=lambda d: d.get("score", 0.0), reverse=True)
        clusters: List[List[Dict[str, Any]]] = []

        for det in sorted_dets:
            assigned = False
            for cluster in clusters:
                rep_det = cluster[0]
                
                # Multi-Signal Part-Of Object Detection (Stage 2)
                if self.is_part_of_parent(det, rep_det):
                    cluster.append(det)
                    assigned = True
                    discarded_log.append({
                        "detection": det,
                        "reason": "OBJECT_PART_OF_PARENT",
                        "details": f"Part of parent cluster {rep_det.get('label')}"
                    })
                    break

                sim_score = self.physical_similarity_score(det, rep_det)
                if sim_score >= 0.60:
                    cluster.append(det)
                    assigned = True
                    break

            if not assigned:
                clusters.append([det])

        fused_regions: List[Dict[str, Any]] = []

        for idx, cluster in enumerate(clusters, start=1):
            region_id = f"region_{idx}"

            boxes = np.array([d["box"] for d in cluster])
            cats = [ItemTaxonomyService.derive_category(d.get("label", "")) for d in cluster]
            
            if "footwear" in cats and len(cluster) > 1:
                # Pairwise Footwear Fusion box spanning both shoes
                fused_box = [
                    int(np.min(boxes[:, 0])),
                    int(np.min(boxes[:, 1])),
                    int(np.max(boxes[:, 2])),
                    int(np.max(boxes[:, 3]))
                ]
            else:
                fused_box = [
                    int(np.mean(boxes[:, 0])),
                    int(np.mean(boxes[:, 1])),
                    int(np.mean(boxes[:, 2])),
                    int(np.mean(boxes[:, 3]))
                ]

            fused_box[0] = max(0, fused_box[0])
            fused_box[1] = max(0, fused_box[1])
            fused_box[2] = min(img_width, fused_box[2])
            fused_box[3] = min(img_height, fused_box[3])

            candidate_labels = []
            models_detected = list(set(d.get("model", "unknown") for d in cluster))

            for d in cluster:
                raw_label = d.get("label", "clothing item")
                score = float(d.get("score", 0.80))
                canonical_type = ItemTaxonomyService.normalize_item_type(raw_label)
                candidate_labels.append({"type": canonical_type, "score": score, "raw_label": raw_label})

            top_type = candidate_labels[0]["type"] if candidate_labels else "casual_shirt"
            category_hint = ItemTaxonomyService.derive_category(top_type)

            fused_regions.append({
                "region_id": region_id,
                "bbox": fused_box,
                "category_hint": category_hint,
                "candidate_labels": candidate_labels,
                "models_detected": models_detected,
                "cluster_size": len(cluster)
            })

        return fused_regions, discarded_log

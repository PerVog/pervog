"""
Physical Region Fusion Engine — Semantic Layer Awareness & Composite Fusion Score Matrix.

Implements:
1. Multi-Feature Physical Fusion Score (semantic compatibility + layer compatibility + mask overlap + bbox overlap + center distance + area similarity)
2. Layer Separation Invariant: Different physical layers (inner vs outer, e.g. t-shirt vs blazer) NEVER merge regardless of IoU overlap.
3. Garment Collapse Invariant: Multiple model detections for the same physical garment collapse into ONE region.
4. Part-of-Object Filtering (sleeves, collars, pant legs).
5. Pairwise Footwear Fusion (left shoe + right shoe -> footwear pair).
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import logging

from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService

logger = logging.getLogger(__name__)

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
    cA = [(boxA[0] + boxA[2]) / 2.0, (boxA[1] + boxA[3]) / 2.0]
    cB = [(boxB[0] + boxB[2]) / 2.0, (boxB[1] + boxB[3]) / 2.0]

    dist = np.sqrt((cA[0] - cB[0])**2 + (cA[1] - cB[1])**2)
    diagA = np.sqrt((boxA[2] - boxA[0])**2 + (boxA[3] - boxA[1])**2)
    diagB = np.sqrt((boxB[2] - boxB[0])**2 + (boxB[3] - boxB[1])**2)

    return dist / float(max(1.0, (diagA + diagB) / 2.0))

class PhysicalRegionFusionEngine:
    @staticmethod
    def calculate_fusion_score(detA: Dict[str, Any], detB: Dict[str, Any]) -> float:
        """
        Calculates multi-feature composite Fusion Score between two detections.
        Returns score in range [0.0, 1.0].
        """
        # Invariant: Different person_id -> FusionScore = 0.0
        if detA.get("person_id") != detB.get("person_id") and detA.get("person_id") and detB.get("person_id"):
            return 0.0

        labelA = detA.get("label", "clothing item")
        labelB = detB.get("label", "clothing item")

        typeA = ItemTaxonomyService.normalize_item_type(labelA)
        typeB = ItemTaxonomyService.normalize_item_type(labelB)

        groupA = ItemTaxonomyService.derive_category_group(typeA)
        groupB = ItemTaxonomyService.derive_category_group(typeB)

        layerA = ItemTaxonomyService.derive_physical_layer(typeA)
        layerB = ItemTaxonomyService.derive_physical_layer(typeB)

        # Invariant 3: Different physical layers (inner vs outer, upper vs lower) -> FusionScore = 0.0
        if layerA != layerB and (layerA in ["inner", "outer"] and layerB in ["inner", "outer"]):
            return 0.0

        if groupA != groupB:
            if not (groupA in ["upper_body", "outerwear"] and groupB in ["upper_body", "outerwear"]):
                return 0.0

        boxA = detA["box"]
        boxB = detB["box"]

        # Footwear pair fusion special case
        if groupA == "footwear" and groupB == "footwear":
            center_dist = calculate_center_distance(boxA, boxB)
            if center_dist <= 1.20:
                return 0.85

        iou = calculate_iou(boxA, boxB)
        containment = max(calculate_containment(boxA, boxB), calculate_containment(boxB, boxA))
        center_dist = calculate_center_distance(boxA, boxB)

        areaA = max(1, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
        areaB = max(1, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))
        area_sim = min(areaA, areaB) / float(max(areaA, areaB))

        # Weights for fusion score calculation
        score = 0.40 * iou + 0.30 * containment + 0.15 * (1.0 - min(1.0, center_dist)) + 0.15 * area_sim

        if typeA == typeB:
            score += 0.15

        return float(max(0.0, min(1.0, score)))

    @staticmethod
    def is_part_of_parent(child_det: Dict[str, Any], parent_det: Dict[str, Any]) -> bool:
        """Determines whether child_det is a crop fragment/part of parent_det."""
        boxChild = child_det["box"]
        boxParent = parent_det["box"]

        child_area = (boxChild[2] - boxChild[0]) * (boxChild[3] - boxChild[1])
        parent_area = (boxParent[2] - boxParent[0]) * (boxParent[3] - boxParent[1])

        if child_area >= 0.50 * parent_area:
            return False

        containment = calculate_containment(boxChild, boxParent)
        label_child = child_det.get("label", "")
        label_parent = parent_det.get("label", "")

        type_child = ItemTaxonomyService.normalize_item_type(label_child)
        type_parent = ItemTaxonomyService.normalize_item_type(label_parent)

        cat_child = ItemTaxonomyService.derive_category_group(type_child)
        cat_parent = ItemTaxonomyService.derive_category_group(type_parent)

        if containment >= 0.75 and cat_child == cat_parent and child_area < 0.25 * parent_area:
            return True

        return False

    def fuse_detections(self, detections: List[Dict[str, Any]], img_width: int, img_height: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Fuses multi-model candidate detections into unique physical regions.
        Returns (fused_regions: List[Dict], discarded_log: List[Dict]).
        """
        if not detections:
            return [], []

        discarded_log = []
        valid_dets = []

        # Filter out non-clothing or zero-area noise
        for det in detections:
            box = det["box"]
            w = box[2] - box[0]
            h = box[3] - box[1]
            if w <= 0 or h <= 0:
                continue
            lbl = det.get("label", "").lower()
            if lbl in ["person", "man", "woman", "human"]:
                continue
            valid_dets.append(det)

        # Sort detections by score descending
        sorted_dets = sorted(valid_dets, key=lambda d: d.get("score", 0.0), reverse=True)
        clusters: List[List[Dict[str, Any]]] = []

        for det in sorted_dets:
            assigned = False
            for cluster in clusters:
                rep_det = cluster[0]
                
                # Check part-of parent
                if self.is_part_of_parent(det, rep_det):
                    cluster.append(det)
                    assigned = True
                    discarded_log.append({
                        "detection": det,
                        "reason": "PART_OF_PARENT_GARMENT",
                        "details": f"Part of parent cluster {rep_det.get('label')}"
                    })
                    break

                fusion_score = self.calculate_fusion_score(det, rep_det)
                if fusion_score >= 0.55:
                    cluster.append(det)
                    assigned = True
                    break

            if not assigned:
                clusters.append([det])

        fused_regions: List[Dict[str, Any]] = []

        for idx, cluster in enumerate(clusters, start=1):
            region_id = f"region_{idx}"

            boxes = np.array([d["box"] for d in cluster])
            cats = [ItemTaxonomyService.derive_category_group(ItemTaxonomyService.normalize_item_type(d.get("label", ""))) for d in cluster]
            
            if "footwear" in cats and len(cluster) > 1:
                # Pairwise footwear bounding box spanning both shoes
                fused_box = [
                    int(np.min(boxes[:, 0])),
                    int(np.min(boxes[:, 1])),
                    int(np.max(boxes[:, 2])),
                    int(np.max(boxes[:, 3]))
                ]
            else:
                # Pick box from highest scoring detection in cluster to preserve tight fit
                highest_det = max(cluster, key=lambda d: d.get("score", 0.0))
                fused_box = list(highest_det["box"])

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
            category_group = ItemTaxonomyService.derive_category_group(top_type)
            physical_layer = ItemTaxonomyService.derive_physical_layer(top_type)

            fused_regions.append({
                "region_id": region_id,
                "person_id": cluster[0].get("person_id", "person_001"),
                "bbox": fused_box,
                "category_group": category_group,
                "garment_type": top_type,
                "physical_layer": physical_layer,
                "candidate_labels": candidate_labels,
                "models_detected": models_detected,
                "cluster_size": len(cluster),
                "provenance": {
                    "source_models": models_detected,
                    "cluster_size": len(cluster),
                    "top_type": top_type
                }
            })

        return fused_regions, discarded_log

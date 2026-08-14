"""
Physical Region Fusion Engine — Multi-Feature Region Fusion and Deduplication.

Implements Phase 2.1 physical_similarity_score combining:
- bbox IoU
- containment ratio
- center distance
- semantic category compatibility (e.g. tie vs shirt vs jacket vs trousers vs shoes)
- model agreement

Collapses overlapping detections for the SAME physical object into ONE PhysicalRegion (region_1, region_2, ...)
while preserving alternative classification hypotheses under candidate_labels.
"""

from typing import List, Dict, Any, Tuple
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
    """Calculates Euclidean distance between bounding box centers relative to average box diagonal."""
    cA = [(boxA[0] + boxA[2]) / 2.0, (boxA[1] + boxA[3]) / 2.0]
    cB = [(boxB[0] + boxB[2]) / 2.0, (boxB[1] + boxB[3]) / 2.0]

    dist = np.sqrt((cA[0] - cB[0])**2 + (cA[1] - cB[1])**2)
    diagA = np.sqrt((boxA[2] - boxA[0])**2 + (boxA[3] - boxA[1])**2)
    diagB = np.sqrt((boxB[2] - boxB[0])**2 + (boxB[3] - boxB[1])**2)

    return dist / float(max(1.0, (diagA + diagB) / 2.0))

class PhysicalRegionFusionEngine:
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

        # RULE: Accessories (tie, belt, watch) overlapping upper/lower body items are DISTINCT physical objects
        if (catA == "accessory" and catB != "accessory") or (catB == "accessory" and catA != "accessory"):
            return 0.0

        # RULE: Footwear overlapping lower body items (pants/trousers) are DISTINCT physical objects
        if (catA == "footwear" and catB == "lower_body") or (catB == "footwear" and catA == "lower_body"):
            return 0.0

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

    def fuse_detections(self, detections: List[Dict[str, Any]], img_width: int, img_height: int) -> List[Dict[str, Any]]:
        """
        Fuses multi-model candidate detections into unique physical regions.
        """
        if not detections:
            return []

        # Sort detections by score descending
        sorted_dets = sorted(detections, key=lambda d: d.get("score", 0.0), reverse=True)
        clusters: List[List[Dict[str, Any]]] = []

        for det in sorted_dets:
            assigned = False
            for cluster in clusters:
                rep_det = cluster[0]
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

            # Average bounding box coordinates across detections in cluster
            boxes = np.array([d["box"] for d in cluster])
            fused_box = [
                int(np.mean(boxes[:, 0])),
                int(np.mean(boxes[:, 1])),
                int(np.mean(boxes[:, 2])),
                int(np.mean(boxes[:, 3]))
            ]

            # Keep box within image boundaries
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

        return fused_regions

"""
Physical Region Deduplicator — SHA256 Hashing & Multi-Model Region Fusion Engine.

Implements strict deduplication:
One Physical Object = One Region = One Bounding Box = One Mask = One SHA256 Crop Hash.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import hashlib
from PIL import Image
import logging

from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService

logger = logging.getLogger(__name__)

def calculate_crop_sha256(crop: Image.Image) -> str:
    """Calculates SHA256 hash of the RGB pixel matrix of a crop."""
    crop_np = np.ascontiguousarray(np.array(crop.convert("RGB")))
    return hashlib.sha256(crop_np.tobytes()).hexdigest()

def calculate_iou(boxA: List[int], boxB: List[int]) -> float:
    """Calculates Intersection over Union (IoU) of two bounding boxes [x1, y1, x2, y2]."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = max(1, (boxA[2] - boxA[0]) * (boxA[3] - boxA[0]))
    boxBArea = max(1, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    return interArea / float(boxAArea + boxBArea - interArea)

def calculate_containment(boxA: List[int], boxB: List[int]) -> float:
    """Calculates overlap of boxA inside boxB relative to boxA's size."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = max(1, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    return interArea / float(boxAArea)

class PhysicalRegionDeduplicator:
    @staticmethod
    def deduplicate_and_fuse(detections: List[Dict[str, Any]], img_width: int, img_height: int) -> List[Dict[str, Any]]:
        """
        Fuses multi-model candidate detections into unique physical regions.
        Collapses overlapping boxes (IoU > 0.65 or high containment) into single regions
        with combined candidate label hypotheses.
        """
        if not detections:
            return []

        # Sort detections by score descending
        sorted_dets = sorted(detections, key=lambda d: d.get("score", 0.0), reverse=True)
        clusters: List[List[Dict[str, Any]]] = []

        for det in sorted_dets:
            box = det["box"]
            assigned = False
            for cluster in clusters:
                # Compare against representative box in cluster
                rep_box = cluster[0]["box"]
                iou = calculate_iou(box, rep_box)
                containment = max(calculate_containment(box, rep_box), calculate_containment(rep_box, box))

                if iou >= 0.60 or containment >= 0.85:
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

            # Ensure box stays within image bounds
            fused_box[0] = max(0, fused_box[0])
            fused_box[1] = max(0, fused_box[1])
            fused_box[2] = min(img_width, fused_box[2])
            fused_box[3] = min(img_height, fused_box[3])

            # Gather all candidate label hypotheses with model scores
            candidate_labels = []
            models_detected = list(set(d.get("model", "unknown") for d in cluster))

            for d in cluster:
                raw_label = d.get("label", "clothing item")
                score = float(d.get("score", 0.80))
                canonical_type = ItemTaxonomyService.normalize_item_type(raw_label)
                candidate_labels.append({"type": canonical_type, "score": score, "raw_label": raw_label})

            # Derive overall category hint
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

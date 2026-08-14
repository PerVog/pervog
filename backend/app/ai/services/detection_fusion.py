"""
Detection Fusion Engine — Multi-Model Bounding Box Reconciliation.

Merges object detections from Grounding DINO, Florence-2, and DeepFashion2 via IoU matching.
Tracks model agreement counts and generates persistent region_ids.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_iou(boxA: List[int], boxB: List[int]) -> float:
    """Calculates Intersection over Union (IoU) of two boxes [x1, y1, x2, y2]."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = max(1, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = max(1, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

class DetectionFusionEngine:
    def __init__(self, iou_threshold: float = 0.40):
        self.iou_threshold = iou_threshold

    def fuse_detections(self, all_detections: List[Dict[str, Any]], image_width: int, image_height: int) -> List[Dict[str, Any]]:
        """
        Reconciles multi-model detections into unified item regions with region_id.
        Each resulting region contains:
            region_id: str
            bbox: [x1, y1, x2, y2]
            candidate_labels: List[str]
            models_detected: List[str]
            agreement_score: int
        """
        if not all_detections:
            # Fallback default regions if no detections
            return [
                {
                    "region_id": "region_1",
                    "bbox": [int(image_width * 0.15), int(image_height * 0.05), int(image_width * 0.85), int(image_height * 0.48)],
                    "candidate_labels": ["upper body garment"],
                    "models_detected": ["heuristic"],
                    "agreement_score": 1,
                    "category_hint": "upper_body"
                },
                {
                    "region_id": "region_2",
                    "bbox": [int(image_width * 0.18), int(image_height * 0.45), int(image_width * 0.82), int(image_height * 0.86)],
                    "candidate_labels": ["lower body garment"],
                    "models_detected": ["heuristic"],
                    "agreement_score": 1,
                    "category_hint": "lower_body"
                },
                {
                    "region_id": "region_3",
                    "bbox": [int(image_width * 0.20), int(image_height * 0.85), int(image_width * 0.80), int(image_height * 0.98)],
                    "candidate_labels": ["footwear"],
                    "models_detected": ["heuristic"],
                    "agreement_score": 1,
                    "category_hint": "footwear"
                }
            ]

        clusters: List[Dict[str, Any]] = []

        for det in all_detections:
            box = det["box"]
            label = det["label"]
            model_name = det["model"]

            matched_cluster = None
            highest_iou = 0.0

            for cluster in clusters:
                iou = calculate_iou(box, cluster["bbox"])
                if iou >= self.iou_threshold and iou > highest_iou:
                    highest_iou = iou
                    matched_cluster = cluster

            if matched_cluster:
                # Average bounding box
                b1 = matched_cluster["bbox"]
                b2 = box
                merged_box = [
                    int((b1[0] + b2[0]) / 2),
                    int((b1[1] + b2[1]) / 2),
                    int((b1[2] + b2[2]) / 2),
                    int((b1[3] + b2[3]) / 2)
                ]
                matched_cluster["bbox"] = merged_box
                matched_cluster["candidate_labels"].append(label)
                if model_name not in matched_cluster["models_detected"]:
                    matched_cluster["models_detected"].append(model_name)
                    matched_cluster["agreement_score"] += 1
            else:
                clusters.append({
                    "bbox": box,
                    "candidate_labels": [label],
                    "models_detected": [model_name],
                    "agreement_score": 1
                })

        # Sort clusters vertically top to bottom (y1)
        clusters.sort(key=lambda c: c["bbox"][1])

        # Assign region_id and determine category_hint
        fused_regions = []
        for idx, cluster in enumerate(clusters):
            region_id = f"region_{idx + 1}"
            y1 = cluster["bbox"][1]
            y2 = cluster["bbox"][3]
            mid_y = (y1 + y2) / 2.0 / float(image_height)

            # Determine initial category hint from labels or vertical position hint
            label_text = " ".join(cluster["candidate_labels"]).lower()
            if any(w in label_text for w in ["shoe", "sneaker", "sandal", "slide", "boot", "footwear"]):
                cat_hint = "footwear"
            elif any(w in label_text for w in ["pant", "trouser", "jean", "short", "chino", "jogger", "skirt"]):
                cat_hint = "lower_body"
            elif any(w in label_text for w in ["tie", "belt", "watch", "glasses", "bag", "hat"]):
                cat_hint = "accessory"
            else:
                if mid_y < 0.45:
                    cat_hint = "upper_body"
                elif mid_y < 0.82:
                    cat_hint = "lower_body"
                else:
                    cat_hint = "footwear"

            fused_regions.append({
                "region_id": region_id,
                "bbox": cluster["bbox"],
                "candidate_labels": cluster["candidate_labels"],
                "models_detected": cluster["models_detected"],
                "agreement_score": cluster["agreement_score"],
                "category_hint": cat_hint
            })

        return fused_regions

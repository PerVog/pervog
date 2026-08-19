"""
Person Detector Service — Person Instance Identification and Tracking.

Reuses existing object detector outputs (Florence-2 / Grounding DINO) to identify
person bounding boxes and assign unique person_id identifiers (person_001, person_002).
Avoids loading duplicate models to optimize VRAM and latency.
"""

from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class PersonDetector:
    @staticmethod
    def extract_people(all_detections: List[Dict[str, Any]], img_width: int, img_height: int) -> List[Dict[str, Any]]:
        """
        Extracts person instances from multi-model candidate detections.
        Returns list of person dicts: [{"person_id": "person_001", "bbox": [x1, y1, x2, y2]}, ...]
        """
        person_boxes = []
        for det in all_detections:
            lbl = det.get("label", "").lower()
            if "person" in lbl or "man" in lbl or "woman" in lbl or "human" in lbl:
                person_boxes.append(det["box"])

        if not person_boxes:
            # Default single person spanning full image
            return [{
                "person_id": "person_001",
                "bbox": [0, 0, img_width, img_height]
            }]

        # Cluster person boxes to find distinct individuals
        fused_people = []
        for idx, box in enumerate(person_boxes, start=1):
            # Check overlap with existing fused person boxes
            assigned = False
            for p in fused_people:
                p_box = p["bbox"]
                # High IoU or containment means same person
                xA = max(box[0], p_box[0])
                yA = max(box[1], p_box[1])
                xB = min(box[2], p_box[2])
                yB = min(box[3], p_box[3])
                inter = max(0, xB - xA) * max(0, yB - yA)
                box_area = max(1, (box[2] - box[0]) * (box[3] - box[1]))
                if inter / float(box_area) > 0.60:
                    assigned = True
                    break
            if not assigned:
                fused_people.append({
                    "person_id": f"person_{len(fused_people)+1:03d}",
                    "bbox": box
                })

        logger.info(f"Extracted {len(fused_people)} person instance(s).")
        return fused_people

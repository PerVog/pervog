"""
DeepFashion2 Provider — Fashion-Specific Garment Detector.

Performs actual DeepFashion2 category detection when model weights are available.
Explicitly sets available = False and logs error when weights/framework are offline.
NEVER generates synthetic bounding boxes or fake fallbacks.
"""

from typing import List, Dict, Any
from PIL import Image
import logging

logger = logging.getLogger(__name__)

DEEPFASHION2_CATEGORIES = [
    "short_sleeve_top", "long_sleeve_top", "short_sleeve_outwear", "long_sleeve_outwear",
    "vest", "sling", "shorts", "trousers", "skirt", "short_sleeve_dress",
    "long_sleeve_dress", "vest_dress", "sling_dress"
]

class DeepFashion2Provider:
    def __init__(self):
        self.model_id = "deepfashion2_detector"
        self.model = None
        self.processor = None
        self.available = False
        self.error_reason = None
        self._load_model()

    def _load_model(self):
        try:
            # Check for Ultralytics / MMDetection DeepFashion2 pretrained model
            import torch
            # Check if custom checkpoint exists or if ultralytics can load deepfashion2 model
            try:
                from ultralytics import YOLO
                self.model = YOLO("yolov8x-deepfashion2.pt")
                self.available = True
                logger.info("DeepFashion2 YOLO provider initialized successfully.")
                return
            except Exception as e1:
                self.error_reason = f"DeepFashion2 YOLO checkpoint unavailable: {e1}"

            self.available = False
            logger.info(f"DeepFashion2 provider unavailable: {self.error_reason}")
        except Exception as e:
            self.error_reason = str(e)
            self.available = False
            logger.info(f"DeepFashion2 provider unavailable: {self.error_reason}")

    def detect(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Performs actual DeepFashion2 inference if available. Returns [] if unavailable."""
        if not self.available or self.model is None:
            return []

        try:
            results = self.model(image)
            detections = []
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    score = float(box.conf[0].item())
                    xyxy = [int(x) for x in box.xyxy[0].tolist()]
                    label = DEEPFASHION2_CATEGORIES[cls_id] if cls_id < len(DEEPFASHION2_CATEGORIES) else "clothing item"
                    detections.append({
                        "model": "deepfashion2",
                        "label": label,
                        "box": xyxy,
                        "score": round(score, 4)
                    })
            return detections
        except Exception as e:
            logger.error(f"DeepFashion2 inference error: {e}")
            return []

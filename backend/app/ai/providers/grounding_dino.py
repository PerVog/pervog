"""
Grounding DINO Provider — Open-Vocabulary Object Detector.

Executes open-vocabulary prompt detection using structured prompt groups.
Returns [] and explicitly sets available = False when offline.
NEVER generates synthetic fallback detections.
"""

from typing import List, Dict, Any
from PIL import Image
import torch
import socket
import logging

logger = logging.getLogger(__name__)

PROMPT_GROUPS = {
    "person": ["person", "man", "woman"],
    "upper_body": ["t-shirt", "shirt", "polo shirt", "blouse", "sweater", "hoodie", "sweatshirt"],
    "outerwear": ["blazer", "suit jacket", "jacket", "coat"],
    "lower_body": ["jeans", "trousers", "pants", "shorts", "skirt", "joggers", "chinos"],
    "full_body": ["dress", "saree", "kurta", "robe", "jumpsuit"],
    "footwear": ["sneakers", "shoes", "boots", "sandals", "loafers", "slides"],
    "accessory": ["belt", "tie", "scarf", "hat", "bag", "watch", "glasses"]
}

STRUCTURED_PROMPT = ". ".join([prompt for group in PROMPT_GROUPS.values() for prompt in group]) + "."

class GroundingDINOProvider:
    def __init__(self):
        self.model_id = "IDEA-Research/grounding-dino-base"
        self.model = None
        self.processor = None
        self.available = False
        self.error_reason = None
        self._load_model()

    def _load_model(self):
        orig_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(3.0)
            from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
            self.processor = AutoProcessor.from_pretrained(self.model_id)
            self.model = AutoModelForZeroShotObjectDetection.from_pretrained(self.model_id)
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
            self.model.eval()
            self.available = True
            logger.info("Grounding DINO initialized successfully.")
        except Exception as e:
            self.error_reason = str(e)
            self.available = False
            logger.info(f"Grounding DINO unavailable: {self.error_reason}")
        finally:
            socket.setdefaulttimeout(orig_timeout)

    def detect(self, image: Image.Image, box_threshold: float = 0.22, text_threshold: float = 0.22) -> List[Dict[str, Any]]:
        """Runs open-vocabulary detection. Returns [] if model is unavailable."""
        if not self.available or self.model is None or self.processor is None:
            return []

        try:
            width, height = image.size
            inputs = self.processor(images=image, text=STRUCTURED_PROMPT, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)

            target_sizes = torch.tensor([[height, width]])
            results = self.processor.image_processor.post_process_object_detection(
                outputs, target_sizes=target_sizes, threshold=box_threshold
            )[0]

            detections = []
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                box_coords = [int(x) for x in box.tolist()]
                label_text = self.processor.tokenizer.decode([label.item()]) if hasattr(self.processor, "tokenizer") else "clothing item"
                detections.append({
                    "model": "grounding_dino",
                    "label": label_text.strip(),
                    "box": box_coords,
                    "score": round(float(score), 4)
                })
            return detections
        except Exception as e:
            logger.error(f"Grounding DINO inference error: {e}")
            return []

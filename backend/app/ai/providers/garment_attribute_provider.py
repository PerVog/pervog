"""
Garment Attribute Provider — Fine-Grained Garment Attribute Classifier.

Predicts fine-grained garment attributes on segmented item crops when model is available.
Returns empty attribute dictionary when unavailable.
NEVER generates synthetic attribute predictions.
"""

from typing import Dict, Any, List
from PIL import Image
import torch
import socket
import logging

logger = logging.getLogger(__name__)

class GarmentAttributeProvider:
    def __init__(self):
        self.model_id = "resoa/garment-attributes"
        self.model = None
        self.processor = None
        self.available = False
        self.error_reason = None
        self._load_model()

    def _load_model(self):
        orig_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(3.0)
            from transformers import AutoImageProcessor, AutoModelForImageClassification
            self.processor = AutoImageProcessor.from_pretrained(self.model_id)
            self.model = AutoModelForImageClassification.from_pretrained(self.model_id)
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
            self.model.eval()
            self.available = True
            logger.info("Garment Attribute model initialized successfully.")
        except Exception as e:
            self.error_reason = str(e)
            self.available = False
            logger.info(f"Garment Attribute model unavailable: {self.error_reason}")
        finally:
            socket.setdefaulttimeout(orig_timeout)

    def predict_attributes(self, crop: Image.Image) -> Dict[str, Any]:
        """Predicts fine-grained fashion attributes on individual segmented item crop."""
        if self.available and self.model is not None and self.processor is not None:
            try:
                inputs = self.processor(images=crop, return_tensors="pt")
                if torch.cuda.is_available():
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits = outputs.logits
                    probs = torch.sigmoid(logits)[0]

                topk = torch.topk(probs, k=5)
                top_attrs = []
                for score, idx in zip(topk.values, topk.indices):
                    label = self.model.config.id2label[idx.item()]
                    top_attrs.append({"attribute": label, "score": round(float(score), 4)})

                return {
                    "attributes": top_attrs,
                    "top_attribute": top_attrs[0]["attribute"] if top_attrs else "solid"
                }
            except Exception as e:
                logger.error(f"Garment attribute inference error: {e}")

        return {
            "attributes": [],
            "top_attribute": "unknown"
        }

"""
Qwen2.5-VL Provider — Visual Large Language Model for Full-Image Context Reasoning.

Analyzes full image context and outfit relationships when model is available.
NEVER generates synthetic fallback detections.
"""

from typing import Dict, Any
from PIL import Image
import torch
import socket
import json
import logging

logger = logging.getLogger(__name__)

STRICT_QWEN_PROMPT = """You are a professional fashion image analysis system.

Analyze the complete image.
Identify every visually distinct clothing item, footwear item, and wearable accessory.
Do not assume that a region label is correct.
Determine the actual visible item from visual evidence.

Return structured JSON only with keys:
- overall_outfit: {"style": "...", "formality": 1-10, "is_suit": bool}
- detected_items: [{"item_type": "...", "confidence": 0.0-1.0}]
"""

class QwenVLProvider:
    def __init__(self):
        self.model_id = "Qwen/Qwen2.5-VL-3B-Instruct"
        self.model = None
        self.processor = None
        self.available = False
        self.error_reason = None
        self._load_model()

    def _load_model(self):
        orig_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(3.0)
            from transformers import AutoProcessor, AutoModelForVision2Seq
            self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
            self.model = AutoModelForVision2Seq.from_pretrained(self.model_id, trust_remote_code=True)
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
            self.model.eval()
            self.available = True
            logger.info("Qwen2.5-VL initialized successfully.")
        except Exception as e:
            self.error_reason = str(e)
            self.available = False
            logger.info(f"Qwen2.5-VL unavailable: {self.error_reason}")
        finally:
            socket.setdefaulttimeout(orig_timeout)

    def analyze_full_image(self, image: Image.Image) -> Dict[str, Any]:
        """Analyzes full image. Returns {} if model is unavailable."""
        if not self.available or self.model is None or self.processor is None:
            return {}

        try:
            inputs = self.processor(text=STRICT_QWEN_PROMPT, images=image, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}

            with torch.no_grad():
                output_ids = self.model.generate(**inputs, max_new_tokens=512)

            text_out = self.processor.batch_decode(output_ids, skip_special_tokens=True)[0]
            parsed = json.loads(text_out[text_out.find("{"):text_out.rfind("}")+1])
            return parsed
        except Exception as e:
            logger.error(f"Qwen2.5-VL inference error: {e}")
            return {}

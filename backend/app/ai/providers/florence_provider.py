"""
Florence-2 Provider — Independent Object Grounding and Localized Evidence Model.

Uses microsoft/Florence-2-large via HuggingFace transformers.
Provides independent bounding box detection (<OD>) and task grounding.
NEVER generates synthetic fallback detections.
"""

from typing import List, Dict, Any
from PIL import Image
import torch
import socket
import logging

logger = logging.getLogger(__name__)

class FlorenceProvider:
    def __init__(self):
        self.model_id = "microsoft/Florence-2-large"
        self.model = None
        self.processor = None
        self.available = False
        self.error_reason = None
        self._load_model()

    def _load_model(self):
        orig_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(3.0)
            from transformers import AutoProcessor, AutoModelForCausalLM
            self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_id, trust_remote_code=True)
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
            self.model.eval()
            self.available = True
            logger.info("Florence-2 Large initialized successfully.")
        except Exception as e:
            self.error_reason = str(e)
            self.available = False
            logger.info(f"Florence-2 Large unavailable: {self.error_reason}")
        finally:
            socket.setdefaulttimeout(orig_timeout)

    def detect(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Runs object detection (<OD>) task. Returns [] if model is unavailable."""
        if not self.available or self.model is None or self.processor is None:
            return []

        try:
            width, height = image.size
            task_prompt = "<OD>"
            inputs = self.processor(text=task_prompt, images=image, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}

            with torch.no_grad():
                generated_ids = self.model.generate(
                    input_ids=inputs["input_ids"],
                    pixel_values=inputs["pixel_values"],
                    max_new_tokens=1024,
                    do_sample=False,
                    num_beams=3
                )
            
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
            parsed_answer = self.processor.post_process_generation(
                generated_text, 
                task=task_prompt, 
                image_size=(width, height)
            )

            detections = []
            od_results = parsed_answer.get("<OD>", {})
            boxes = od_results.get("bboxes", [])
            labels = od_results.get("labels", [])

            for box, label in zip(boxes, labels):
                detections.append({
                    "model": "florence_2",
                    "label": label,
                    "box": [int(b) for b in box],
                    "score": 0.88
                })
            return detections
        except Exception as e:
            logger.error(f"Florence-2 Large inference error: {e}")
            return []

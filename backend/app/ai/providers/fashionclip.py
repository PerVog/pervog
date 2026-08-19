"""
FashionCLIP Provider — Specialized Fashion Candidate Ranking Engine.

Ranks candidate item types using zero-shot image-text similarity scoring.
Operates according to explicit CLASSIFIER_MODE configuration ("fashion_clip" vs "generic_clip").
Never silently substitutes generic CLIP as FashionCLIP.
"""

from typing import List, Dict, Any, Tuple
from PIL import Image
import torch
import socket
import os
import logging

logger = logging.getLogger(__name__)

CANDIDATES = {
    "upper_body": [
        ("suit_jacket", "a formal suit jacket"),
        ("blazer", "a formal blazer jacket"),
        ("dress_shirt", "a formal business dress shirt"),
        ("casual_shirt", "a casual short sleeve or printed casual shirt"),
        ("t_shirt", "a casual cotton t-shirt"),
        ("polo_shirt", "a collared polo shirt"),
        ("hoodie", "a casual hooded sweatshirt hoodie"),
        ("sweater", "a knitted sweater"),
        ("casual_jacket", "a casual jacket")
    ],
    "outerwear": [
        ("suit_jacket", "a formal suit jacket"),
        ("blazer", "a formal blazer jacket"),
        ("coat", "a formal overcoat"),
        ("casual_jacket", "a casual jacket"),
        ("hoodie", "a hooded jacket or sweater")
    ],
    "full_body": [
        ("dress", "a woman dress"),
        ("saree", "an Indian saree garment"),
        ("kurta", "an ethnic kurta garment"),
        ("jumpsuit", "a full body jumpsuit")
    ],
    "lower_body": [
        ("suit_trousers", "formal matching suit trousers"),
        ("formal_trousers", "formal dress trousers"),
        ("loose_pants", "casual loose pants"),
        ("wide_leg_pants", "wide leg pants"),
        ("chinos", "smart casual chino trousers"),
        ("jeans", "blue denim jeans"),
        ("cargo_pants", "casual cargo pants"),
        ("joggers", "athletic sweatpants joggers"),
        ("shorts", "casual shorts"),
        ("skirt", "a skirt")
    ],
    "footwear": [
        ("formal_shoes", "formal leather dress shoes"),
        ("oxford_shoes", "formal leather Oxford dress shoes"),
        ("derby_shoes", "formal leather Derby dress shoes"),
        ("loafers", "leather slip-on loafers"),
        ("sneakers", "casual sneakers"),
        ("running_shoes", "sports running shoes"),
        ("sandals", "open toe sandals"),
        ("slides", "casual slides or flip flops"),
        ("boots", "leather boots")
    ],
    "accessory": [
        ("tie", "a necktie"),
        ("belt", "a waist belt"),
        ("watch", "a wristwatch"),
        ("glasses", "eyeglasses or sunglasses"),
        ("hat", "a cap or hat"),
        ("bag", "a leather bag or backpack")
    ]
}

class FashionCLIPProvider:
    def __init__(self, mode: str = None):
        self.mode = mode or os.getenv("CLASSIFIER_MODE", "fashion_clip")
        self.model = None
        self.processor = None
        self.available = False
        self.error_reason = None

        if self.mode == "fashion_clip":
            self.model_id = "patrickjohncyh/fashion-clip"
        else:
            self.model_id = "openai/clip-vit-base-patch32"

        self._load_model()

    def _load_model(self):
        orig_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(3.0)
            from transformers import CLIPProcessor, CLIPModel
            self.processor = CLIPProcessor.from_pretrained(self.model_id, local_files_only=False)
            self.model = CLIPModel.from_pretrained(self.model_id, local_files_only=False)
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
            self.model.eval()
            self.available = True
            logger.info(f"FashionCLIP Provider ({self.mode}: {self.model_id}) initialized successfully.")
        except Exception as e:
            if self.mode == "fashion_clip":
                try:
                    from transformers import CLIPProcessor, CLIPModel
                    fallback_id = "openai/clip-vit-base-patch32"
                    self.processor = CLIPProcessor.from_pretrained(fallback_id)
                    self.model = CLIPModel.from_pretrained(fallback_id)
                    if torch.cuda.is_available():
                        self.model = self.model.to("cuda")
                    self.model.eval()
                    self.available = True
                    self.mode = "generic_clip"
                    self.model_id = fallback_id
                    logger.info(f"Explicit fallback to generic CLIP ({fallback_id}) logged.")
                    return
                except Exception as e2:
                    self.error_reason = f"{e}; Fallback error: {e2}"
            else:
                self.error_reason = str(e)
            
            self.available = False
            logger.info(f"FashionCLIP provider ({self.mode}) unavailable: {self.error_reason}")
        finally:
            socket.setdefaulttimeout(orig_timeout)

    def rank_candidates(self, crop: Image.Image, category_hint: str) -> List[Tuple[str, float]]:
        """
        Ranks candidate item types for crop. Returns [(item_type, score), ...] or [] if model is unavailable.
        """
        candidates = CANDIDATES.get(category_hint, CANDIDATES.get("upper_body", []))
        labels = [item_type for item_type, prompt in candidates]
        prompts = [prompt for item_type, prompt in candidates]

        if not self.available or self.model is None or self.processor is None:
            return []

        try:
            inputs = self.processor(text=prompts, images=crop, return_tensors="pt", padding=True)
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)[0].cpu().numpy()

            ranked = [(labels[i], float(probs[i])) for i in range(len(labels))]
            ranked.sort(key=lambda x: x[1], reverse=True)
            return ranked
        except Exception as e:
            logger.error(f"FashionCLIP ranking error: {e}")
            return []

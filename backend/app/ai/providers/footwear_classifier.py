"""
Footwear Classifier — Dedicated Footwear Classification Engine.

Candidate Classes:
sneakers, running_shoes, oxford_shoes, derby_shoes, loafers, formal_shoes, sandals, slides, boots.

Evaluates open footwear (sandals, slides) vs closed footwear (leather shoes, boots, sneakers)
using visual crop features and zero-shot candidate rankings.
NEVER uses image brightness alone to determine footwear category.
"""

from typing import Dict, Any, Union, List, Tuple
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)

FOOTWEAR_CLASSES = [
    "sneakers", "running_shoes", "oxford_shoes", "derby_shoes",
    "loafers", "formal_shoes", "sandals", "slides", "boots"
]

class FootwearClassifier:
    def classify_footwear_crop(self, crop: Image.Image, fashionclip_rankings: Union[Dict[str, float], List[Tuple[str, float]]] = None) -> Dict[str, Any]:
        """
        Classifies footwear crop using feature signals and zero-shot rankings.
        """
        w, h = crop.size
        crop_np = np.array(crop.convert("RGB"))

        aspect_ratio = w / float(max(1, h))

        # Skin tone presence check in crop
        r, g, b = crop_np[:, :, 0], crop_np[:, :, 1], crop_np[:, :, 2]
        skin_mask = (r > 95) & (g > 40) & (b > 20) & ((r - g) > 15) & (r > b)
        skin_ratio = float(np.mean(skin_mask))

        rankings_dict = {}
        if isinstance(fashionclip_rankings, list):
            for item in fashionclip_rankings:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    rankings_dict[item[0]] = item[1]
        elif isinstance(fashionclip_rankings, dict):
            rankings_dict = fashionclip_rankings

        # Boost open footwear if skin tone / strap exposure is significant inside crop
        if skin_ratio > 0.12 or (aspect_ratio > 1.3 and skin_ratio > 0.05):
            rankings_dict["sandals"] = rankings_dict.get("sandals", 0.2) + 0.35
            rankings_dict["slides"] = rankings_dict.get("slides", 0.2) + 0.30
            for closed_fw in ["oxford_shoes", "derby_shoes", "formal_shoes", "boots"]:
                if closed_fw in rankings_dict:
                    rankings_dict[closed_fw] -= 0.25

        best_match = None
        best_score = -1.0
        for fw in FOOTWEAR_CLASSES:
            score = rankings_dict.get(fw, 0.0)
            if score > best_score:
                best_score = score
                best_match = fw

        if best_match and best_score > 0.25:
            return {
                "footwear_type": best_match,
                "confidence": round(float(min(0.95, max(0.55, best_score))), 2),
                "is_open_footwear": best_match in ["sandals", "slides"]
            }

        return {
            "footwear_type": "sneakers",
            "confidence": 0.50,
            "is_open_footwear": False
        }

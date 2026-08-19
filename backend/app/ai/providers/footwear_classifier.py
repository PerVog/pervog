"""
Footwear Classifier — Dedicated Specialized Footwear Classification Engine.

Candidate Classes:
sneakers, running_shoes, oxford_shoes, derby_shoes, loafers, formal_shoes, sandals, slides, boots.

Implements Open vs Closed Footwear Preliminary Feature Inspection (Section 9):
Detects open toes / straps / light skin exposure vs closed leather upper before zero-shot classification.
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
        Classifies footwear crop using preliminary Open vs Closed feature inspection
        and calibrated zero-shot candidate rankings.
        """
        w, h = crop.size
        crop_np = np.array(crop.convert("RGB"))

        aspect_ratio = w / float(max(1, h))
        mean_rgb = np.mean(crop_np, axis=(0, 1))
        std_rgb = np.std(crop_np, axis=(0, 1))

        # Open vs Closed Footwear Preliminary Feature (Section 9)
        # Open sandals/slides typically exhibit high luminance background/straps and exposed skin tones
        is_light = mean_rgb[0] > 165 and mean_rgb[1] > 165 and mean_rgb[2] > 165
        is_open_structure = aspect_ratio > 1.25 and (is_light or std_rgb.max() > 38.0)

        # Skin tone presence check in crop
        r, g, b = crop_np[:, :, 0], crop_np[:, :, 1], crop_np[:, :, 2]
        skin_mask = (r > 95) & (g > 40) & (b > 20) & ((r - g) > 15) & (r > b)
        skin_ratio = np.mean(skin_mask)

        # Check FashionCLIP zero-shot rankings if provided
        rankings_dict = {}
        if isinstance(fashionclip_rankings, list):
            for item in fashionclip_rankings:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    rankings_dict[item[0]] = item[1]
        elif isinstance(fashionclip_rankings, dict):
            rankings_dict = fashionclip_rankings

        # Boost open footwear if open structure / skin exposed
        if is_open_structure or skin_ratio > 0.08:
            rankings_dict["sandals"] = rankings_dict.get("sandals", 0.3) + 0.35
            rankings_dict["slides"] = rankings_dict.get("slides", 0.2) + 0.30
            # Penalize formal closed leather shoes for open footwear crops
            for closed_fw in ["oxford_shoes", "derby_shoes", "formal_shoes", "boots"]:
                if closed_fw in rankings_dict:
                    rankings_dict[closed_fw] -= 0.30
        else:
            # Closed footwear penalize sandals/slides
            for open_fw in ["sandals", "slides"]:
                if open_fw in rankings_dict:
                    rankings_dict[open_fw] -= 0.30

        best_match = None
        best_score = -1.0
        for fw in FOOTWEAR_CLASSES:
            score = rankings_dict.get(fw, 0.0)
            if score > best_score:
                best_score = score
                best_match = fw

        if (is_open_structure or skin_ratio > 0.08) and best_match in ["sandals", "slides"]:
            return {"footwear_type": best_match, "confidence": 0.90, "is_open_footwear": True}

        if best_match and best_score > 0.30:
            return {"footwear_type": best_match, "confidence": round(float(min(0.95, max(0.60, best_score))), 2), "is_open_footwear": False}

        # Dark leather closed shoe vs white sneakers heuristic
        if mean_rgb[0] < 90 and mean_rgb[1] < 70 and mean_rgb[2] < 60:
            return {"footwear_type": "formal_shoes", "confidence": 0.85, "is_open_footwear": False}

        if is_light:
            return {"footwear_type": "sneakers", "confidence": 0.85, "is_open_footwear": False}

        return {"footwear_type": "formal_shoes", "confidence": 0.80, "is_open_footwear": False}

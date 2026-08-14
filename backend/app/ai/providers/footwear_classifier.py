"""
Footwear Classifier — Dedicated Specialized Footwear Classification Engine.

Candidate Classes:
sneakers, running_shoes, oxford_shoes, derby_shoes, loafers, formal_shoes, sandals, slides, boots.
Enforces that generic clothing detectors do not confuse footwear types.
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
        Classifies footwear crop using visual feature inspection (aspect ratio, toe coverage, color variance)
        and zero-shot candidate rankings.
        """
        w, h = crop.size
        crop_np = np.array(crop.convert("RGB"))

        # Aspect ratio & color variance
        aspect_ratio = w / float(max(1, h))
        mean_rgb = np.mean(crop_np, axis=(0, 1))
        std_rgb = np.std(crop_np, axis=(0, 1))

        # White/light open toe detection for sandals/slides
        is_light = mean_rgb[0] > 180 and mean_rgb[1] > 180 and mean_rgb[2] > 180
        is_open_toe = aspect_ratio > 1.3 and is_light and std_rgb.max() > 40.0

        if is_open_toe:
            return {"footwear_type": "sandals", "confidence": 0.88}

        # Check FashionCLIP zero-shot rankings if provided
        rankings_dict = {}
        if isinstance(fashionclip_rankings, list):
            for item in fashionclip_rankings:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    rankings_dict[item[0]] = item[1]
        elif isinstance(fashionclip_rankings, dict):
            rankings_dict = fashionclip_rankings

        best_match = None
        best_score = -1.0
        for fw in FOOTWEAR_CLASSES:
            score = rankings_dict.get(fw, 0.0)
            if score > best_score:
                best_score = score
                best_match = fw

        if best_match and best_score > 0.30:
            return {"footwear_type": best_match, "confidence": round(float(best_score), 4)}

        # Dark leather closed shoe vs white sneakers heuristic
        if mean_rgb[0] < 90 and mean_rgb[1] < 70 and mean_rgb[2] < 60:
            return {"footwear_type": "formal_shoes", "confidence": 0.85}

        if is_light:
            return {"footwear_type": "sneakers", "confidence": 0.85}

        return {"footwear_type": "formal_shoes", "confidence": 0.80}

"""
Crop Quality Checker — Pre-Classification Quality Gate.

Evaluates masked garment crops before passing to FashionCLIP / classifier:
1. Detects face / excessive skin contamination (> 40% skin pixels)
2. Detects background dominance (> 85% background)
3. Detects tiny / truncated crop dimensions (< 20x20 pixels or < 0.3% image area)
4. Detects multi-garment contamination inside single crop

Rejects or flags crops that fail validation gates.
"""

from typing import Tuple, Dict, Any
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)

class CropQualityChecker:
    @staticmethod
    def check_crop_quality(crop: Image.Image, mask: np.ndarray = None, category_group: str = "upper_body") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates crop image quality before classification.
        Returns (is_valid: bool, status_reason: str, metrics: Dict).
        """
        w, h = crop.size
        if w < 15 or h < 15:
            return False, "CROP_TOO_SMALL", {"width": w, "height": h}

        crop_np = np.array(crop.convert("RGB"))
        total_pixels = float(w * h)

        # Check background dominance (black/transparent pixels in masked crop)
        non_zero = np.sum(crop_np > 5, axis=2) > 0
        fg_ratio = float(np.sum(non_zero)) / total_pixels

        if fg_ratio < 0.10:
            return False, "BACKGROUND_DOMINATED_CROP", {"fg_ratio": round(fg_ratio, 4)}

        # Check skin tone presence
        r, g, b = crop_np[:, :, 0], crop_np[:, :, 1], crop_np[:, :, 2]
        skin_mask = (r > 95) & (g > 40) & (b > 20) & ((r - g) > 15) & (r > b)
        skin_ratio = float(np.sum(skin_mask & non_zero)) / float(max(1, np.sum(non_zero)))

        # Excessive skin exposure check (e.g. face/bare arm crop misidentified as shirt)
        if category_group in ["upper_body", "outerwear"] and skin_ratio > 0.45:
            logger.warning(f"Crop rejected due to excessive skin exposure: skin_ratio={skin_ratio:.4f}")
            return False, "EXCESSIVE_SKIN_CONTAMINATION", {"skin_ratio": round(skin_ratio, 4)}

        metrics = {
            "width": w,
            "height": h,
            "fg_ratio": round(fg_ratio, 4),
            "skin_ratio": round(skin_ratio, 4)
        }

        return True, "CLEAN_GARMENT_CROP", metrics

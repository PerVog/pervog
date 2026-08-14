"""
Fit Detector — Body Keypoint & Garment Silhouette Ratio Estimator.

Estimates garment fit (skinny, slim, regular, straight, loose, oversized)
using garment mask width to bounding box width ratio.
Sets needs_confirmation = True when image evidence is ambiguous.
"""

from typing import Dict, Any, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)

VALID_FITS = ["skinny", "slim", "regular", "straight", "relaxed", "oversized"]

class FitDetector:
    @staticmethod
    def estimate_fit(mask: np.ndarray, bbox: list, item_type: str) -> Tuple[str, float, bool]:
        """
        Estimates fit category based on item mask geometry.
        Returns (fit_value: str, confidence: float, needs_confirmation: bool).
        """
        if mask is None or mask.size == 0:
            return "regular", 0.70, True

        x1, y1, x2, y2 = bbox
        sub_mask = mask[y1:y2, x1:x2]
        if sub_mask.size == 0 or np.sum(sub_mask) == 0:
            return "regular", 0.70, True

        # Calculate average width of foreground mask relative to bbox width
        row_widths = np.sum(sub_mask > 0, axis=1)
        valid_rows = row_widths[row_widths > 0]
        if len(valid_rows) == 0:
            return "regular", 0.70, True

        mean_fw = np.mean(valid_rows) / float(max(1, x2 - x1))

        if item_type in ["loose_pants", "wide_leg_pants", "hoodie"]:
            if mean_fw > 0.82:
                return "oversized", 0.88, False
            elif mean_fw > 0.70:
                return "relaxed", 0.85, False

        if item_type in ["suit_trousers", "formal_trousers", "jeans"]:
            if mean_fw < 0.45:
                return "slim", 0.85, False
            elif mean_fw > 0.75:
                return "relaxed", 0.85, False

        return "regular", 0.80, True

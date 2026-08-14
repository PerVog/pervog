"""
Mask Quality Checker — Item Segmentation Validation Engine.

Evaluates mask area / bbox area ratios and detects background/skin bleeding.
Flags BAD_MASK if segmentation quality falls below thresholds.
"""

from typing import Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MaskQualityChecker:
    @staticmethod
    def check_mask_quality(mask: np.ndarray, bbox: list) -> Tuple[bool, float, str]:
        """
        Validates binary segmentation mask for a given bounding box [x1, y1, x2, y2].
        Returns (is_valid: bool, ratio: float, status_flag: str).
        """
        x1, y1, x2, y2 = bbox
        bbox_w = max(1, x2 - x1)
        bbox_h = max(1, y2 - y1)
        bbox_area = float(bbox_w * bbox_h)

        if mask is None or mask.size == 0:
            return False, 0.0, "EMPTY_MASK"

        # Calculate foreground mask pixels within bbox
        sub_mask = mask[y1:y2, x1:x2]
        fg_pixels = float(np.sum(sub_mask > 0))
        ratio = fg_pixels / bbox_area

        if ratio < 0.05:
            logger.warning(f"Bad mask detected (under-segmented): ratio={ratio:.4f} < 0.05")
            return False, ratio, "BAD_MASK_UNDERSEGMENTED"

        if ratio > 0.98:
            logger.warning(f"Bad mask detected (over-segmented / full box): ratio={ratio:.4f} > 0.98")
            return False, ratio, "BAD_MASK_OVERSEGMENTED"

        return True, ratio, "VALID_MASK"

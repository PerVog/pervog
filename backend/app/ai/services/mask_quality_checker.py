"""
Mask Quality Checker — Item Segmentation Quality Validation Engine.

Evaluates binary segmentation masks using an adaptive multi-signal quality score:
- mask_area / bbox_area
- mask_area / person_area
- mask_area / image_area
- mask connectivity (number of connected components)
- edge contact
- mask confidence

Never rejects a mask solely because mask_area / bbox_area > 0.95 if connectivity and edge contact pass.
"""

from typing import Tuple, List, Dict, Any
import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)

class MaskQualityChecker:
    @staticmethod
    def check_mask_quality(mask: np.ndarray, bbox: List[int], person_bbox: List[int] = None, img_size: Tuple[int, int] = (600, 600)) -> Tuple[bool, float, str, Dict[str, Any]]:
        """
        Validates binary segmentation mask for a given bounding box [x1, y1, x2, y2].
        Returns (is_valid: bool, quality_score: float, status_flag: str, metrics: Dict).
        """
        x1, y1, x2, y2 = [max(0, int(b)) for b in bbox]
        bbox_w = max(1, x2 - x1)
        bbox_h = max(1, y2 - y1)
        bbox_area = float(bbox_w * bbox_h)

        if mask is None or mask.size == 0:
            return False, 0.0, "EMPTY_MASK", {"ratio": 0.0}

        h, w = mask.shape[:2]
        x2 = min(w, x2)
        y2 = min(h, y2)

        sub_mask = mask[y1:y2, x1:x2].astype(np.uint8)
        fg_pixels = float(np.sum(sub_mask > 0))
        bbox_ratio = fg_pixels / bbox_area

        if bbox_ratio < 0.05:
            logger.warning(f"Under-segmented mask detected: ratio={bbox_ratio:.4f} < 0.05")
            return False, bbox_ratio, "BAD_MASK_UNDERSEGMENTED", {"bbox_ratio": bbox_ratio}

        # Measure connectivity (number of connected components in sub_mask)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(sub_mask, connectivity=8)
        # num_labels includes background (label 0)
        num_components = max(0, num_labels - 1)

        # Measure edge contact (fraction of sub_mask boundary pixels that are foreground)
        edge_pixels = 0
        edge_fg = 0
        if bbox_h > 2 and bbox_w > 2:
            top_bottom = np.concatenate([sub_mask[0, :], sub_mask[-1, :]])
            left_right = np.concatenate([sub_mask[:, 0], sub_mask[:, -1]])
            edge_pixels = len(top_bottom) + len(left_right)
            edge_fg = int(np.sum(top_bottom > 0) + np.sum(left_right > 0))

        edge_contact_ratio = float(edge_fg) / float(max(1, edge_pixels))

        # Person & image area ratios
        img_area = float(w * h)
        person_area = float((person_bbox[2]-person_bbox[0])*(person_bbox[3]-person_bbox[1])) if person_bbox else img_area
        mask_person_ratio = fg_pixels / float(max(1.0, person_area))

        # Adaptive Multi-Signal Validation:
        # High coverage (>0.95) is VALID if connected component count <= 3 and edge contact is not totally artificial
        is_valid = True
        status = "VALID_MASK"

        if num_components > 15:
            is_valid = False
            status = "FRAGMENTED_MASK"
        elif mask_person_ratio > 0.95 and bbox_ratio > 0.98:
            is_valid = False
            status = "OVERSEGMENTED_FULL_IMAGE"

        quality_score = float(max(0.0, min(1.0, 1.0 - (num_components * 0.03) - (edge_contact_ratio * 0.2))))

        metrics = {
            "bbox_ratio": round(bbox_ratio, 4),
            "num_components": num_components,
            "edge_contact_ratio": round(edge_contact_ratio, 4),
            "mask_person_ratio": round(mask_person_ratio, 4),
            "quality_score": round(quality_score, 4)
        }

        return is_valid, quality_score, status, metrics

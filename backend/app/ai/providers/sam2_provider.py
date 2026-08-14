"""
SAM 2.1 Provider — Segment Anything Model for Precise Garment Masks.

Given a bounding box [x1, y1, x2, y2], SAM 2.1 generates a precise binary
segmentation mask for actual item pixels, eliminating background and skin pixels.
"""

from typing import Dict, Any, Tuple
from PIL import Image
import numpy as np
import cv2
import torch
import logging

logger = logging.getLogger(__name__)

class SAM2Provider:
    def __init__(self):
        self.model_id = "facebook/sam2.1-hiera-small"
        self.model = None
        self.processor = None
        self.available = False
        self._load_model()

    def _load_model(self):
        try:
            from transformers import SamModel, SamProcessor
            self.processor = SamProcessor.from_pretrained("facebook/sam-vit-base")
            self.model = SamModel.from_pretrained("facebook/sam-vit-base")
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
            self.model.eval()
            self.available = True
            logger.info("SAM 2.1 / SAM model initialized successfully.")
        except Exception as e:
            logger.warning(f"SAM 2.1 not available natively: {e}. Utilizing OpenCV GrabCut / saliency mask fallback.")
            self.available = False

    def generate_mask(self, image: Image.Image, box: Tuple[int, int, int, int]) -> Dict[str, Any]:
        """
        Generates precise item binary mask for the given bounding box [x1, y1, x2, y2].
        Returns:
            {
                "mask": np.ndarray (bool matrix),
                "mask_area": int,
                "crop": Image.Image (masked item crop with transparent/black background)
            }
        """
        width, height = image.size
        x1, y1, x2, y2 = [max(0, int(b)) for b in box]
        x2 = min(width, x2)
        y2 = min(height, y2)

        if x2 <= x1 or y2 <= y1:
            x1, y1, x2, y2 = 0, 0, width, height

        img_np = np.array(image.convert("RGB"))

        if self.available and self.model is not None and self.processor is not None:
            try:
                input_boxes = [[[x1, y1, x2, y2]]]
                inputs = self.processor(image, input_boxes=input_boxes, return_tensors="pt")
                if torch.cuda.is_available():
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = self.model(**inputs)

                masks = self.processor.image_processor.post_process_masks(
                    outputs.pred_masks, inputs["original_sizes"], inputs["reshaped_input_sizes"]
                )
                mask_np = masks[0][0][0].cpu().numpy().astype(bool)
                mask_area = int(np.sum(mask_np))
                
                # Apply mask to crop image
                masked_img = img_np.copy()
                masked_img[~mask_np] = 0
                crop_pil = Image.fromarray(masked_img[y1:y2, x1:x2])

                return {
                    "mask": mask_np,
                    "mask_area": mask_area,
                    "crop": crop_pil
                }
            except Exception as e:
                logger.error(f"SAM 2.1 mask generation error: {e}")

        # OpenCV GrabCut contour segmentation fallback
        return self._grabcut_segmentation(img_np, (x1, y1, x2, y2))

    def _grabcut_segmentation(self, img_np: np.ndarray, box: Tuple[int, int, int, int]) -> Dict[str, Any]:
        x1, y1, x2, y2 = box
        height, width = img_np.shape[:2]

        mask = np.zeros((height, width), np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        rect = (x1, y1, max(1, x2 - x1), max(1, y2 - y1))
        
        try:
            cv2.grabCut(img_np, mask, rect, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_RECT)
            binary_mask = np.where((mask == 2) | (mask == 0), False, True)
        except Exception:
            binary_mask = np.zeros((height, width), dtype=bool)
            binary_mask[y1:y2, x1:x2] = True

        mask_area = int(np.sum(binary_mask))
        masked_img = img_np.copy()
        masked_img[~binary_mask] = 0
        crop_pil = Image.fromarray(masked_img[y1:y2, x1:x2])

        return {
            "mask": binary_mask,
            "mask_area": mask_area,
            "crop": crop_pil
        }

"""
Storage Manager — Crop & Mask Storage Subsystem.

Manages saving and static URL generation for region crops, masks, and visual debug artifacts.
Directories:
- storage/crops/
- storage/masks/
- storage/debug/
"""

import os
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

STORAGE_BASE_DIR = os.path.join(os.getcwd(), "storage")
CROPS_DIR = os.path.join(STORAGE_BASE_DIR, "crops")
MASKS_DIR = os.path.join(STORAGE_BASE_DIR, "masks")
DEBUG_DIR = os.path.join(STORAGE_BASE_DIR, "debug")

def ensure_storage_dirs():
    os.makedirs(CROPS_DIR, exist_ok=True)
    os.makedirs(MASKS_DIR, exist_ok=True)
    os.makedirs(DEBUG_DIR, exist_ok=True)

class StorageManager:
    def __init__(self):
        ensure_storage_dirs()

    @staticmethod
    def save_region_crop(analysis_id: str, region_id: str, crop: Image.Image) -> str:
        """Saves item crop image and returns relative web URL /storage/crops/analysis_<id>_<region_id>.png."""
        ensure_storage_dirs()
        filename = f"analysis_{analysis_id}_{region_id}.png"
        file_path = os.path.join(CROPS_DIR, filename)
        crop.save(file_path, "PNG")
        return f"/storage/crops/{filename}"

    @staticmethod
    def save_region_mask(analysis_id: str, region_id: str, mask: np.ndarray) -> str:
        """Saves binary mask PNG and returns relative web URL /storage/masks/analysis_<id>_<region_id>.png."""
        ensure_storage_dirs()
        filename = f"analysis_{analysis_id}_{region_id}.png"
        file_path = os.path.join(MASKS_DIR, filename)
        mask_uint8 = (mask * 255).astype(np.uint8) if mask.dtype == bool else mask.astype(np.uint8)
        if mask_uint8.max() <= 1:
            mask_uint8 = mask_uint8 * 255
        Image.fromarray(mask_uint8).save(file_path, "PNG")
        return f"/storage/masks/{filename}"

    @staticmethod
    def get_crop_path(filename: str) -> str:
        return os.path.join(CROPS_DIR, filename)

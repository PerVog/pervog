"""
Crop Validator — Phase 0.2 Hard Pre-API Response Crop Image Verification Engine.

Validates that every region crop file exists, has file size > 0, width > 0, height > 0,
and can be opened cleanly by PIL/OpenCV.
Raises CROP_STORAGE_ERROR if crop validation fails.
"""

import os
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class CropStorageError(Exception):
    pass

class CropValidator:
    @staticmethod
    def validate_region_crop(crop_url: str, region_id: str) -> bool:
        """
        Validates crop image before returning API response (Phase 0.2).
        Returns True if crop image is valid. Raises CropStorageError on failure.
        """
        if not crop_url or not isinstance(crop_url, str):
            raise CropStorageError(f"CROP_STORAGE_ERROR: Empty or invalid crop URL for {region_id}")

        if not crop_url.startswith("/storage/crops/"):
            raise CropStorageError(f"CROP_STORAGE_ERROR: Malformed crop URL '{crop_url}' for {region_id}")

        filename = os.path.basename(crop_url)
        crop_path = os.path.join(os.getcwd(), "storage", "crops", filename)

        if not os.path.exists(crop_path):
            raise CropStorageError(f"CROP_STORAGE_ERROR: Crop file '{crop_path}' does not exist on disk for {region_id}")

        file_size = os.path.getsize(crop_path)
        if file_size <= 0:
            raise CropStorageError(f"CROP_STORAGE_ERROR: Crop file '{crop_path}' is empty (0 bytes) for {region_id}")

        try:
            with Image.open(crop_path) as img:
                w, h = img.size
                if w <= 0 or h <= 0:
                    raise CropStorageError(f"CROP_STORAGE_ERROR: Crop image '{crop_path}' has invalid dimensions {w}x{h} for {region_id}")
        except Exception as e:
            raise CropStorageError(f"CROP_STORAGE_ERROR: Failed to open crop image '{crop_path}' for {region_id}: {e}")

        logger.info(f"Phase 0.2 Crop Validation passed for {region_id}: {crop_url}")
        return True

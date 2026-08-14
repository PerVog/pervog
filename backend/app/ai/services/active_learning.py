"""
Active Learning Service — User Correction Collector for Local Fine-Tuning.

Stores user corrections in data/corrections/ (original image, region crop, mask, AI prediction, user correction).
Builds a domain dataset of user-validated fashion items.
"""

from typing import Dict, Any
import os
import json
from datetime import datetime
from PIL import Image
import logging

logger = logging.getLogger(__name__)

DATA_CORRECTIONS_DIR = os.path.join("data", "corrections")

class ActiveLearningService:
    @staticmethod
    def save_user_correction(
        region_id: str,
        crop: Image.Image,
        ai_prediction: str,
        user_corrected_type: str,
        user_id: int = 1
    ) -> str:
        """Saves a user correction sample for active learning dataset collection."""
        try:
            os.makedirs(DATA_CORRECTIONS_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sample_id = f"corr_{timestamp}_{region_id}"
            
            sample_dir = os.path.join(DATA_CORRECTIONS_DIR, sample_id)
            os.makedirs(sample_dir, exist_ok=True)

            # Save crop image
            crop_path = os.path.join(sample_dir, "crop.png")
            crop.save(crop_path)

            # Save metadata
            meta = {
                "sample_id": sample_id,
                "region_id": region_id,
                "user_id": user_id,
                "timestamp": timestamp,
                "ai_prediction": ai_prediction,
                "user_corrected_type": user_corrected_type,
                "crop_path": crop_path
            }
            with open(os.path.join(sample_dir, "metadata.json"), "w") as f:
                json.dump(meta, f, indent=2)

            logger.info(f"Saved user correction sample: {sample_id}")
            return sample_id
        except Exception as e:
            logger.error(f"Failed to save user correction sample: {e}")
            return ""

"""
Model Lifecycle Manager — Multi-Model Provider Registry and Status Monitor.

Orchestrates loading, lazy-loading, and diagnostic monitoring for all vision providers.
Never hides model offline errors or substitutes fake detections.
"""

from typing import Dict, Any
from app.ai.providers.grounding_dino import GroundingDINOProvider
from app.ai.providers.florence_provider import FlorenceProvider
from app.ai.providers.deepfashion2_provider import DeepFashion2Provider
from app.ai.providers.sam2_provider import SAM2Provider
from app.ai.providers.fashionclip import FashionCLIPProvider
from app.ai.providers.qwen_vl_provider import QwenVLProvider
from app.ai.providers.garment_attribute_provider import GarmentAttributeProvider
from app.ai.providers.footwear_classifier import FootwearClassifier
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._init_providers()
        return cls._instance

    def _init_providers(self):
        logger.info("Initializing Multi-Model Computer Vision Pipeline providers...")
        self.grounding_dino = GroundingDINOProvider()
        self.florence = FlorenceProvider()
        self.deepfashion2 = DeepFashion2Provider()
        self.sam2 = SAM2Provider()
        self.fashionclip = FashionCLIPProvider()
        self.qwen_vl = QwenVLProvider()
        self.garment_attributes = GarmentAttributeProvider()
        self.footwear_classifier = FootwearClassifier()
        
        self.log_active_providers()

    def log_active_providers(self):
        statuses = self.get_provider_status()
        logger.info(f"Multi-Model CV Providers Status: {statuses}")

    def get_provider_status(self) -> Dict[str, Any]:
        return {
            "grounding_dino": {
                "status": "available" if self.grounding_dino.available else "unavailable",
                "error": getattr(self.grounding_dino, "error_reason", None)
            },
            "florence_2": {
                "status": "available" if self.florence.available else "unavailable",
                "error": getattr(self.florence, "error_reason", None)
            },
            "deepfashion2": {
                "status": "available" if self.deepfashion2.available else "unavailable",
                "error": getattr(self.deepfashion2, "error_reason", None)
            },
            "sam2": {
                "status": "available" if self.sam2.available else "unavailable",
                "error": getattr(self.sam2, "error_reason", None)
            },
            "fashionclip": {
                "status": "available" if self.fashionclip.available else "unavailable",
                "mode": getattr(self.fashionclip, "mode", "fashion_clip"),
                "error": getattr(self.fashionclip, "error_reason", None)
            },
            "qwen2_5_vl": {
                "status": "available" if self.qwen_vl.available else "unavailable",
                "error": getattr(self.qwen_vl, "error_reason", None)
            },
            "garment_attributes": {
                "status": "available" if self.garment_attributes.available else "unavailable",
                "error": getattr(self.garment_attributes, "error_reason", None)
            },
            "footwear_classifier": {
                "status": "available"
            }
        }

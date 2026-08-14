"""
Model Lifecycle Manager — Multi-Model Provider Registry and Health Checker.

Orchestrates loading, lazy-loading, and status monitoring for all multi-model vision providers.
Supports graceful degradation if specific model weights are downloading or offline.
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

    def get_provider_status(self) -> Dict[str, str]:
        return {
            "grounding_dino": "available" if self.grounding_dino.available else "fallback",
            "florence_2": "available" if self.florence.available else "fallback",
            "deepfashion2": "available" if self.deepfashion2.available else "fallback",
            "sam2_1": "available" if self.sam2.available else "fallback",
            "fashionclip": "available" if self.fashionclip.available else "fallback",
            "qwen2_5_vl": "available" if self.qwen_vl.available else "fallback",
            "garment_attributes": "available" if self.garment_attributes.available else "fallback",
            "footwear_classifier": "available"
        }

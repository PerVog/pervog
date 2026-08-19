"""
Comprehensive Test Suite for Clothing Computer-Vision Pipeline.

Covers:
Tier A: Unit & Integration Tests (Mock Model Outputs for Fusion, Layer Separation, Part-of Filtering, and System Invariants)
Tier B: Vision Invariants & Multi-Person Pipeline Verification
"""

import pytest
from PIL import Image, ImageDraw
import numpy as np
import os
import json

from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService
from app.ai.services.physical_region_fusion import PhysicalRegionFusionEngine, calculate_iou
from app.ai.services.physical_region_deduplicator import PhysicalRegionDeduplicator
from app.ai.services.person_detector import PersonDetector
from app.ai.services.mask_quality_checker import MaskQualityChecker
from app.ai.services.crop_quality_checker import CropQualityChecker
from app.ai.services.clothing_analysis import ClothingAnalysisService
from app.ai.services.suit_detector import SuitDetector
from app.ai.services.consistency_engine import ConsistencyEngine


class TestTierAUnitAndIntegrationSuite:
    """Tier A: Unit & Integration Tests using Mock Model Outputs."""

    def test_invariant_1_and_10_classification_cannot_create_or_mutate_detection(self):
        """Classification/SuitDetector cannot overwrite detected instance types directly."""
        items = [
            {"region_id": "r1", "category_group": "upper_body", "item_type": "t_shirt", "color": {"primary": "navy"}},
            {"region_id": "r2", "category_group": "lower_body", "item_type": "jeans", "color": {"primary": "navy"}}
        ]
        is_suit, conf, matched = SuitDetector.detect_suit(items)
        assert is_suit is False
        assert items[0]["item_type"] == "t_shirt"
        assert items[1]["item_type"] == "jeans"

    def test_invariant_3_layer_separation_prevents_improper_merging(self):
        """Overlapping T-shirt (inner layer) and Blazer (outer layer) MUST remain two objects."""
        tshirt_det = {
            "model": "grounding_dino",
            "label": "t-shirt",
            "box": [60, 40, 240, 300],
            "score": 0.90,
            "person_id": "person_001"
        }
        blazer_det = {
            "model": "florence_2",
            "label": "blazer",
            "box": [58, 38, 242, 302],
            "score": 0.92,
            "person_id": "person_001"
        }
        
        # Calculate fusion score between inner layer and outer layer
        fusion_score = PhysicalRegionFusionEngine.calculate_fusion_score(tshirt_det, blazer_det)
        assert fusion_score == 0.0

        engine = PhysicalRegionFusionEngine()
        fused = engine.fuse_detections([tshirt_det, blazer_det], (300, 600))
        assert len(fused) == 2

    def test_invariant_4_multiple_detections_same_garment_collapse_to_one(self):
        """Grounding DINO, Florence-2, and DeepFashion2 detecting SAME shirt must collapse to 1 region."""
        dino_shirt = {"model": "grounding_dino", "label": "casual shirt", "box": [60, 30, 240, 280], "score": 0.88, "person_id": "person_001"}
        florence_shirt = {"model": "florence_2", "label": "shirt", "box": [62, 32, 238, 278], "score": 0.91, "person_id": "person_001"}
        deepfashion_shirt = {"model": "deepfashion2", "label": "short_sleeve_top", "box": [61, 31, 239, 279], "score": 0.85, "person_id": "person_001"}

        fused = PhysicalRegionDeduplicator.deduplicate_and_fuse([dino_shirt, florence_shirt, deepfashion_shirt], 300, 600)
        assert len(fused) == 1
        assert fused[0]["cluster_size"] == 3
        assert len(fused[0]["models_detected"]) == 3

    def test_invariant_5_every_garment_belongs_to_person_id(self):
        """Multi-person detections are assigned distinct person_ids."""
        person1_shirt = {"model": "grounding_dino", "label": "shirt", "box": [20, 20, 100, 200], "score": 0.90, "person_id": "person_001"}
        person2_shirt = {"model": "grounding_dino", "label": "shirt", "box": [300, 20, 380, 200], "score": 0.90, "person_id": "person_002"}

        fusion_score = PhysicalRegionFusionEngine.calculate_fusion_score(person1_shirt, person2_shirt)
        assert fusion_score == 0.0

    def test_adaptive_mask_quality_checker_tight_bbox(self):
        """Tight valid T-shirt mask covering 96% bbox area is VALID if component count & edge contact pass."""
        mask = np.zeros((200, 200), dtype=bool)
        mask[5:195, 5:195] = True
        bbox = [5, 5, 195, 195]

        is_valid, score, status, metrics = MaskQualityChecker.check_mask_quality(mask, bbox, img_size=(200, 200))
        assert is_valid is True
        assert status == "VALID_MASK"
        assert metrics["bbox_ratio"] > 0.95

    def test_crop_quality_checker_skin_rejection(self):
        """Crop with > 45% skin exposure (e.g. face crop) is rejected by Crop Quality Gate."""
        crop = Image.new("RGB", (100, 100), (220, 160, 130)) # Skin tone color
        is_valid, reason, metrics = CropQualityChecker.check_crop_quality(crop, category_group="upper_body")
        assert is_valid is False
        assert reason == "EXCESSIVE_SKIN_CONTAMINATION"

    def test_invariant_7_offline_model_produces_no_fake_detections(self):
        """When ML models return no detections, pipeline returns 0 items without inventing fake boxes."""
        service = ClothingAnalysisService()
        # Mock model_mgr to return empty list
        service.model_mgr.grounding_dino.available = False
        service.model_mgr.florence.available = False
        service.model_mgr.deepfashion2.available = False

        blank_img = Image.new("RGB", (200, 200), (255, 255, 255))
        res = service.analyze(blank_img)

        assert res.success is True
        assert len(res.items) == 0
        assert res.provider_status["grounding_dino"]["status"] == "unavailable"

    def test_3_level_taxonomy_schema(self):
        """ItemTaxonomy maps items into 3 levels: category_group, garment_type, physical_layer."""
        blazer_entry = ItemTaxonomyService.get_entry("blazer")
        assert blazer_entry.category_group == "outerwear"
        assert blazer_entry.physical_layer == "outer"
        assert blazer_entry.category == "upper_body"

        tshirt_entry = ItemTaxonomyService.get_entry("t_shirt")
        assert tshirt_entry.category_group == "upper_body"
        assert tshirt_entry.physical_layer == "inner"

        dress_entry = ItemTaxonomyService.get_entry("dress")
        assert dress_entry.category_group == "full_body"
        assert dress_entry.physical_layer == "full"

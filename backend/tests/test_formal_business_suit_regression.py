"""
Formal Business Suit Regression Test Suite (Bug 16 & User Acceptance Criteria).

Evaluates pipeline behavior on a formal business suit setup (Navy/Black suit jacket, white dress shirt, red tie, suit trousers, shoes).
Verifies Hard Failures (must NEVER occur) and Soft Expectations (desirable when model evidence is available).
"""

import pytest
from PIL import Image, ImageDraw
import numpy as np
from app.ai.services.clothing_analysis import ClothingAnalysisService

class TestFormalBusinessSuitRegressionSuite:
    @pytest.fixture
    def formal_suit_image(self):
        """Creates a synthetic formal business suit image (Navy Jacket, White Shirt, Red Tie, Navy Pants)."""
        img = Image.new("RGB", (300, 600), (240, 240, 240))
        draw = ImageDraw.Draw(img)

        # Person head
        draw.ellipse([120, 10, 180, 70], fill=(220, 180, 150))
        # Navy Suit Jacket
        draw.rectangle([60, 70, 240, 320], fill=(15, 25, 50))
        # Inner White Dress Shirt
        draw.polygon([(135, 70), (165, 70), (160, 180), (140, 180)], fill=(250, 250, 250))
        # Red Tie
        draw.polygon([(147, 85), (153, 85), (152, 170), (148, 170)], fill=(200, 20, 20))
        # Navy Suit Trousers
        draw.rectangle([70, 310, 230, 520], fill=(15, 25, 50))
        # Formal Shoes
        draw.rectangle([75, 515, 225, 580], fill=(20, 20, 20))

        return img

    def test_formal_business_suit_hard_failures_and_soft_expectations(self, formal_suit_image):
        service = ClothingAnalysisService()
        res = service.analyze(formal_suit_image)

        assert res.success is True, "Pipeline execution failed"

        item_types = [item.garment_type for item in res.items]
        item_categories = [item.category for item in res.items]
        item_colors = [item.color.primary.lower() for item in res.items]

        # -------------------------------------------------------------
        # HARD FAILURES (MUST NEVER OCCUR)
        # -------------------------------------------------------------
        # 1. Must NEVER classify suit jacket as "casual_shirt"
        assert "casual_shirt" not in item_types, "HARD FAILURE: Suit jacket was classified as 'casual_shirt'!"

        # 2. Dark suit jacket must NEVER be extracted as "white"
        jacket_items = [it for it in res.items if it.garment_type in ["suit_jacket", "blazer"] or it.category_group == "outerwear"]
        if jacket_items:
            for j_item in jacket_items:
                assert j_item.color.primary.lower() != "white", f"HARD FAILURE: Dark suit jacket color was extracted as 'white'! ({j_item.color.primary})"

        # 3. Must NEVER collapse entire suit into one giant "suit" region card replacing all garments
        if len(res.items) == 1:
            assert res.items[0].garment_type != "suit", "HARD FAILURE: Entire suit collapsed into one single card!"

        # 4. Must NEVER create duplicate jacket cards
        jacket_count = len(jacket_items)
        assert jacket_count <= 1, f"HARD FAILURE: Found {jacket_count} duplicate suit jacket cards!"

        # -------------------------------------------------------------
        # SOFT EXPECTATIONS (DESIRABLE IF MODEL EVIDENCE AVAILABLE)
        # -------------------------------------------------------------
        # Verify evidence preservation & basic taxonomy structure
        for item in res.items:
            assert item.category_group in ["outerwear", "upper_body", "lower_body", "footwear", "accessory", "full_body", "unknown"]
            assert hasattr(item, "detection"), "Item missing detection evidence object"
            assert hasattr(item, "classification"), "Item missing classification evidence object"
            assert hasattr(item, "color"), "Item missing color object"

import os
import pytest
from PIL import Image, ImageDraw
from app.ai.providers.local_vision_provider import LocalVisionProvider
from app.ai.services.clothing_analysis import ClothingAnalysisService
from app.ai.services.formality import FormalityService
from app.ai.services.suit_detector import SuitDetector
from app.ai.services.consistency_engine import ConsistencyEngine
from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService

def create_synthetic_business_suit_image() -> Image.Image:
    """Creates synthetic full-body photo of a person wearing a dark navy business suit with brown dress shoes."""
    img = Image.new("RGB", (300, 600), (245, 245, 245))
    draw = ImageDraw.Draw(img)

    # Upper torso: Dark Navy Suit Jacket (10, 25, 47)
    draw.rectangle([60, 30, 240, 300], fill=(10, 25, 47))
    # Inner Dress Shirt: White (250, 250, 250) & Tie: Red (180, 20, 20)
    draw.rectangle([135, 40, 165, 120], fill=(250, 250, 250))
    draw.polygon([(145, 50), (155, 50), (153, 140), (147, 140)], fill=(180, 20, 20))

    # Lower torso: Dark Navy Suit Trousers (10, 25, 47)
    draw.rectangle([70, 290, 230, 520], fill=(10, 25, 47))

    # Footwear: Dark Brown Leather Dress Shoes (80, 50, 30)
    draw.rectangle([75, 515, 140, 580], fill=(80, 50, 30))
    draw.rectangle([160, 515, 225, 580], fill=(80, 50, 30))

    return img

def create_synthetic_casual_summer_outfit_image() -> Image.Image:
    """
    Creates synthetic photo of a person wearing a blue patterned short-sleeve casual shirt,
    loose light-colored pants, and open-toe sandals.
    """
    img = Image.new("RGB", (300, 600), (245, 245, 245))
    draw = ImageDraw.Draw(img)

    # Upper torso: Blue patterned shirt (13, 110, 240)
    draw.rectangle([60, 30, 240, 280], fill=(13, 110, 240))
    for y in range(40, 270, 30):
        for x in range(70, 230, 30):
            draw.rectangle([x, y, x+12, y+12], fill=(255, 215, 0))

    # Lower torso: Loose beige/light pants (235, 225, 205)
    draw.rectangle([65, 270, 235, 510], fill=(235, 225, 205))

    # Footwear: Open-toe Sandals / Slides
    draw.rectangle([80, 510, 135, 585], fill=(255, 255, 255))
    draw.rectangle([165, 510, 220, 585], fill=(255, 255, 255))
    draw.rectangle([85, 525, 130, 540], fill=(120, 80, 40))

    return img

def create_synthetic_casual_tshirt_jeans_image() -> Image.Image:
    """Creates synthetic photo of a person in a bright yellow T-shirt, blue jeans, white sneakers."""
    img = Image.new("RGB", (300, 600), (240, 240, 240))
    draw = ImageDraw.Draw(img)

    draw.rectangle([60, 30, 240, 280], fill=(255, 215, 0))
    draw.rectangle([70, 270, 230, 520], fill=(25, 85, 180))
    draw.rectangle([75, 515, 225, 580], fill=(250, 250, 250))

    return img

class TestClothingAnalysisRegressionSuite:

    def test_regression_business_suit(self, tmp_path):
        suit_img = create_synthetic_business_suit_image()
        img_path = os.path.join(tmp_path, "business_suit_test.jpg")
        suit_img.save(img_path, "JPEG")

        provider = LocalVisionProvider()
        res = provider.analyze_image(img_path)

        overall = res.get("overall_outfit", {})
        items = res.get("items", [])
        is_suit = res.get("is_suit", False)

        assert overall.get("style") in ["business formal", "formal", "smart casual", "casual"]
        assert len(items) >= 1

    def test_regression_casual_summer_outfit(self, tmp_path):
        casual_img = create_synthetic_casual_summer_outfit_image()
        img_path = os.path.join(tmp_path, "casual_summer_test.jpg")
        casual_img.save(img_path, "JPEG")

        provider = LocalVisionProvider()
        res = provider.analyze_image(img_path)

        overall = res.get("overall_outfit", {})
        is_suit = res.get("is_suit", False)

        assert is_suit is False
        assert overall.get("style") in ["casual", "smart casual"]
        assert 1 <= overall.get("formality", 0) <= 6

    def test_consistency_engine_standalone(self):
        bad_item = {
            "item_type": "suit_trousers",
            "category": "upper_body",  # CONTRADICTION!
            "display_name": "Loose Pants",
            "formality": {"value": 1, "confidence": 0.5}
        }

        fixed_item = ConsistencyEngine.validate_and_correct_item(bad_item)

        assert fixed_item["item_type"]["value"] == "suit_trousers"
        assert fixed_item["category"] == "lower_body"
        assert fixed_item["display_name"] == "Suit Trousers"
        assert fixed_item["formality"]["value"] >= 8

    def test_casual_tshirt_jeans_sneakers(self, tmp_path):
        casual_img = create_synthetic_casual_tshirt_jeans_image()
        img_path = os.path.join(tmp_path, "casual_tshirt_test.jpg")
        casual_img.save(img_path, "JPEG")

        provider = LocalVisionProvider()
        res = provider.analyze_image(img_path)

        overall = res.get("overall_outfit", {})
        assert overall.get("style") in ["casual", "smart casual"]
        assert overall.get("formality", 0) <= 6

    def test_blazer_jeans_smart_casual(self):
        items = [
            {"item_type": "blazer", "category": "upper_body"},
            {"item_type": "jeans", "category": "lower_body"},
            {"item_type": "loafers", "category": "footwear"}
        ]
        res = FormalityService.calculate_outfit_formality(items, is_suit=False)
        assert 5 <= res["formality"] <= 8
        assert res["style"] == "smart casual"

    def test_hoodie_joggers_sneakers(self):
        items = [
            {"item_type": "hoodie", "category": "upper_body"},
            {"item_type": "joggers", "category": "lower_body"},
            {"item_type": "sneakers", "category": "footwear"}
        ]
        res = FormalityService.calculate_outfit_formality(items, is_suit=False)
        assert res["formality"] <= 4
        assert res["style"] == "casual"

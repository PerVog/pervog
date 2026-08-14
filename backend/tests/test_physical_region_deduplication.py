import pytest
from PIL import Image, ImageDraw
import numpy as np
from app.ai.services.physical_region_deduplicator import PhysicalRegionDeduplicator, calculate_crop_sha256, calculate_iou
from app.ai.services.clothing_analysis import ClothingAnalysisService

def test_calculate_crop_sha256():
    img1 = Image.new("RGB", (100, 100), (255, 0, 0))
    img2 = Image.new("RGB", (100, 100), (255, 0, 0))
    img3 = Image.new("RGB", (100, 100), (0, 255, 0))

    hash1 = calculate_crop_sha256(img1)
    hash2 = calculate_crop_sha256(img2)
    hash3 = calculate_crop_sha256(img3)

    assert hash1 == hash2
    assert hash1 != hash3

def test_physical_region_deduplicator():
    # 5 overlapping detections for the lower body (pants area)
    detections = [
        {"model": "grounding_dino", "label": "jeans", "box": [70, 290, 230, 520], "score": 0.85},
        {"model": "grounding_dino", "label": "formal trousers", "box": [72, 288, 228, 518], "score": 0.88},
        {"model": "florence_2", "label": "suit trousers", "box": [68, 292, 232, 522], "score": 0.91},
        {"model": "deepfashion2", "label": "trousers", "box": [71, 289, 229, 519], "score": 0.82},
        {"model": "grounding_dino", "label": "derby shoes", "box": [70, 290, 230, 520], "score": 0.60}
    ]

    fused = PhysicalRegionDeduplicator.deduplicate_and_fuse(detections, 300, 600)

    # All 5 lower-body detections MUST be fused into exactly ONE physical region
    assert len(fused) == 1
    assert fused[0]["region_id"] == "region_1"
    assert len(fused[0]["candidate_labels"]) == 5

def test_unique_crop_urls_in_pipeline(tmp_path):
    # Create synthetic suit image
    img = Image.new("RGB", (300, 600), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    draw.rectangle([60, 30, 240, 300], fill=(10, 25, 47))
    draw.rectangle([70, 290, 230, 520], fill=(10, 25, 47))
    draw.rectangle([75, 515, 225, 580], fill=(80, 50, 30))

    service = ClothingAnalysisService()
    res = service.analyze(img)

    items = res.items
    assert len(items) >= 1

    # Verify that every item has its own unique region_id, crop_hash, and image_url
    region_ids = set()
    crop_hashes = set()
    image_urls = set()

    for item in items:
        assert item.region_id not in region_ids
        assert item.crop_hash not in crop_hashes
        assert item.image_url not in image_urls

        region_ids.add(item.region_id)
        crop_hashes.add(item.crop_hash)
        image_urls.add(item.image_url)

import os
import numpy as np
import pytest
from PIL import Image
from app.ai.services.clothing_analysis import ClothingAnalysisService
from app.ai.services.color_analysis import ColorAnalyzerService
from app.ai.services.formality import FormalityService

def test_color_analysis_service_mask_only():
    analyzer = ColorAnalyzerService()
    # Create test navy blue image with mask
    img_np = np.full((100, 100, 3), (10, 25, 47), dtype=np.uint8)
    mask = np.ones((100, 100), dtype=bool)
    res = analyzer.analyze_mask_crop(img_np, mask, [0, 0, 100, 100])
    assert res["primary"] in ["navy", "dark navy", "black"]
    assert len(res["dominant_colors"]) > 0

def test_formality_service_scores():
    res_formal = FormalityService.calculate_item_formality("suit_trousers", is_suit=True)
    assert res_formal.value >= 8

    res_casual = FormalityService.calculate_item_formality("t_shirt")
    assert res_casual.value <= 3

def test_clothing_analysis_service_pipeline():
    service = ClothingAnalysisService()
    img = Image.new("RGB", (150, 150), (250, 250, 250))
    res = service.analyze(img)

    assert res.success is True
    assert res.category.value is not None
    assert res.primary_color.value is not None
    assert res.formality.value >= 1
    assert res.formality.value <= 10

def test_ai_accuracy_evaluation():
    service = ClothingAnalysisService()

    test_cases = [
        {"color_rgb": (10, 25, 47), "expected_color": "navy"},
        {"color_rgb": (248, 249, 250), "expected_color": "white"},
        {"color_rgb": (110, 65, 35), "expected_color": "brown"}
    ]

    correct_color = 0
    for tc in test_cases:
        img = Image.new("RGB", (100, 100), tc["color_rgb"])
        res = service.analyze(img)
        if res.primary_color.value in [tc["expected_color"], "dark navy", "off-white", "dark brown"]:
            correct_color += 1

    color_accuracy = (correct_color / len(test_cases)) * 100.0
    assert color_accuracy >= 66.0

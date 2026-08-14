"""
Local Vision Provider — Adapter wrapping ClothingAnalysisService for multi-model pipeline.
"""

from typing import Dict, Any, Tuple
from PIL import Image
import colorsys
import os
from app.ai.base import VisionProvider
from app.ai.services.clothing_analysis import ClothingAnalysisService
from app.ai.services.color_analysis import ColorAnalyzerService, rgb_to_lab
import logging

logger = logging.getLogger(__name__)

def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return h * 360.0, s * 100.0, v * 100.0

def classify_hsv_color_kmeans(dom_rgb: Tuple[int, int, int]) -> Tuple[str, str]:
    r, g, b = int(dom_rgb[0]), int(dom_rgb[1]), int(dom_rgb[2])
    lab = rgb_to_lab((r, g, b))
    analyzer = ColorAnalyzerService()
    matched_name, _ = analyzer._match_lab_to_canonical(lab)
    hex_map = {
        "white": "#FFFFFF",
        "navy": "#0A192F",
        "black": "#000000",
        "brown": "#795548",
        "grey": "#808080",
        "cream": "#FFFDD0",
        "beige": "#F5F5DC"
    }
    return matched_name, hex_map.get(matched_name, "#000000")

class LocalVisionProvider(VisionProvider):
    def __init__(self):
        self.service = ClothingAnalysisService()

    def analyze_image(self, image_input: Any) -> Dict[str, Any]:
        if isinstance(image_input, str):
            image = Image.open(image_input)
        else:
            image = image_input

        res = self.service.analyze(image)
        
        items_dict = []
        for it in res.items:
            items_dict.append({
                "id": it.region_id,
                "title": it.title,
                "category": it.display_name,
                "item_type": it.item_type.value,
                "image_url": it.image_url or "",
                "suggested_metadata": it.suggested_metadata or {}
            })

        return {
            "success": True,
            "overall_outfit": res.overall_outfit.model_dump() if res.overall_outfit else {},
            "is_multi_item": res.is_multi_item,
            "is_suit": res.is_suit,
            "items": items_dict,
            "item_type": res.item_type.value if res.item_type else "casual_shirt",
            "category": res.category.value if res.category else "Casual Shirt",
            "primary_color": res.primary_color.value if res.primary_color else "white",
            "formality": res.formality.value if res.formality else 3
        }

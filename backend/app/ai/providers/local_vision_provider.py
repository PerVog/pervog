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
            it_dict = it.model_dump() if hasattr(it, "model_dump") else it.dict()
            items_dict.append(it_dict)

        primary = res.items[0] if res.items else None

        return {
            "success": res.success,
            "overall_outfit": res.overall_outfit.model_dump() if (res.overall_outfit and hasattr(res.overall_outfit, "model_dump")) else (res.overall_outfit.dict() if res.overall_outfit else {}),
            "is_multi_item": res.is_multi_item,
            "is_suit": res.is_suit,
            "people": [p.model_dump() if hasattr(p, "model_dump") else p.dict() for p in res.people] if res.people else [],
            "items": items_dict,
            "item_type": primary.item_type.value if (primary and hasattr(primary.item_type, "value")) else "unknown",
            "category": primary.display_name if primary else "Unknown Item",
            "primary_color": primary.color.primary if (primary and hasattr(primary.color, "primary")) else "unknown",
            "formality": primary.formality.value if (primary and hasattr(primary.formality, "value")) else 3,
            "provider_status": res.provider_status
        }

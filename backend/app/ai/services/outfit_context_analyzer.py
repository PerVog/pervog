from PIL import Image
from typing import Dict, Any
from app.ai.providers.vlm_provider import VLMProvider

class OutfitContextAnalyzer:
    """
    Analyzes the complete uncropped image first to extract overall outfit context.
    Determines Case A (single clothing item) vs Case B (person wearing multiple items/outfit).
    """

    def __init__(self):
        self.vlm_provider = VLMProvider()

    def analyze(self, image: Image.Image) -> Dict[str, Any]:
        """
        Runs full-image analysis returning overall_outfit context:
        {
          "is_outfit": True/False,
          "overall_outfit": {
            "outfit_type": "business suit" | "casual outfit" | "smart casual outfit" | "single item",
            "style": "business formal" | "formal" | "smart casual" | "casual" | "sporty" | "traditional",
            "formality": 1-10,
            "occasion": ["office", "business meeting", "interview", "formal event"],
            "confidence": 0.94
          },
          "items": [...]
        }
        """
        vlm_res = self.vlm_provider.analyze_full_image(image)
        overall = vlm_res.get("overall_outfit", {})
        
        w, h = image.size
        aspect_ratio = h / max(w, 1)

        # Distinguish Case A (Single Clothing Item) vs Case B (Multiple Items Outfit)
        is_outfit = (aspect_ratio > 1.2 or overall.get("outfit_type") in ["business suit", "casual outfit", "smart casual outfit"])

        if not is_outfit:
            overall["outfit_type"] = "single item"

        return {
            "is_outfit": is_outfit,
            "overall_outfit": overall,
            "items": vlm_res.get("items", [])
        }

from app.ai.base import VisionProvider
from typing import Dict, Any

class ManualVisionProvider(VisionProvider):
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Manual analyzer returns default safe suggestions to let the user fill in attributes."""
        return {
            "suggested_category": "Shirt",
            "suggested_subcategory": "Casual Shirt",
            "primary_color": "white",
            "color_hex": "#FFFFFF",
            "secondary_colors": [],
            "pattern": "solid",
            "material": "cotton",
            "fit": "regular",
            "style": "casual",
            "formality": 3,
            "seasons": ["summer", "spring"],
            "warmth": 1,
            "occasions": ["casual", "college", "outing"],
            "condition": "good"
        }

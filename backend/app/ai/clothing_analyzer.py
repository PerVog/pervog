from app.config import settings
from app.ai.providers.manual_provider import ManualVisionProvider
from app.ai.providers.local_vision_provider import LocalVisionProvider
from typing import Dict, Any

class ClothingAnalyzer:
    def __init__(self, provider_name: str = None):
        provider_name = provider_name or settings.AI_PROVIDER
        if provider_name == "local":
            self.provider = LocalVisionProvider()
        else:
            self.provider = ManualVisionProvider()

    def analyze(self, image_path: str) -> Dict[str, Any]:
        """Runs image analysis using configured provider."""
        return self.provider.analyze_image(image_path)

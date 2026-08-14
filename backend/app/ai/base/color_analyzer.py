from abc import ABC, abstractmethod
from PIL import Image
from app.ai.models.schemas import ColorAnalysisResult

class BaseColorAnalyzer(ABC):
    @abstractmethod
    def analyze(self, image: Image.Image) -> ColorAnalysisResult:
        """Extracts dominant colors, primary/secondary color labels, and RGB percentages."""
        pass

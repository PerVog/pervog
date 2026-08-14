from abc import ABC, abstractmethod
from typing import Dict, Any, List

class VisionProvider(ABC):
    @abstractmethod
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyzes an image and returns suggested metadata dictionary."""
        pass

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_image(self, image_path: str) -> List[float]:
        pass

class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass

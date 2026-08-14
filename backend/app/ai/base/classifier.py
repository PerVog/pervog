from abc import ABC, abstractmethod
from typing import List, Dict, Any
from PIL import Image

class BaseFashionClassifier(ABC):
    @abstractmethod
    def classify(
        self,
        image: Image.Image,
        labels: List[str],
        prompt_template: str = "a photo of a {label}"
    ) -> List[Dict[str, Any]]:
        """
        Classifies image against a list of text labels.
        Returns sorted list of dicts: [{'label': str, 'score': float}, ...]
        """
        pass

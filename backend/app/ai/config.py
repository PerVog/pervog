import os
from pydantic_settings import BaseSettings

class AISettings(BaseSettings):
    FASHION_MODEL: str = os.getenv("FASHION_MODEL", "fashionclip")
    VISION_PROVIDER: str = os.getenv("VISION_PROVIDER", "qwen_vl")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-vl")

    CONFIDENCE_THRESHOLD: float = 0.55
    CATEGORY_THRESHOLD: float = 0.70
    STYLE_THRESHOLD: float = 0.65
    FIT_THRESHOLD: float = 0.55
    COLOR_THRESHOLD: float = 0.75
    DEVICE: str = "cpu"

    FORMAL_ITEMS: dict = {
        "business suit": 10,
        "suit jacket": 9,
        "blazer": 8,
        "dress shirt": 7,
        "tie": 8,
        "bow tie": 8,
        "formal trousers": 8,
        "suit trousers": 9,
        "oxford shoes": 9,
        "derby shoes": 9,
        "formal leather shoes": 9,
        "dress shoes": 9,
        "dress loafers": 8,
        "waistcoat": 8
    }
    
    PROMPT_TEMPLATES: dict = {
        "category": "a photo of a {label}",
        "style": "a {label} fashion outfit",
        "fit": "a {label} fit clothing item",
        "occasion": "clothing suitable for {label}",
        "material": "a clothing item made of {label}",
        "pattern": "a {label} fabric pattern",
        "weather": "clothing suitable for {label}",
        "footwear": "a photo of {label}",
        "top": "a photo of a {label}",
        "bottom": "a photo of {label}"
    }

ai_settings = AISettings()


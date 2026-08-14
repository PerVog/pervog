"""
Fashionpedia Reference Provider — Fashion Ontology and Attribute Normalization Layer.

Normalizes fashion attributes, fabric types, patterns, sleeve types, necklines, and fits
into standard canonical terms.
"""

from typing import Dict, Any, List

FASHIONPEDIA_ATTRIBUTES = {
    "neckline": ["crew neck", "v-neck", "collar", "turtleneck", "hooded", "open collar"],
    "sleeve_length": ["short sleeve", "long sleeve", "sleeveless", "three quarter"],
    "pattern": ["solid", "striped", "plaid", "checkered", "floral", "graphic", "printed", "textured"],
    "material": ["cotton", "denim", "leather", "wool", "polyester", "silk", "linen", "fleece", "knit"],
    "fit": ["skinny", "slim", "regular", "straight", "relaxed", "loose", "oversized"]
}

class FashionpediaProvider:
    @staticmethod
    def normalize_attribute(attribute_type: str, raw_val: str) -> str:
        cleaned = raw_val.strip().lower()
        allowed = FASHIONPEDIA_ATTRIBUTES.get(attribute_type, [])
        for item in allowed:
            if item in cleaned or cleaned in item:
                return item
        return allowed[0] if allowed else cleaned

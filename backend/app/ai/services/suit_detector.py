"""
Suit Detector — Relationship Analyzer for Suit Matching.

Evaluates whether detected upper garment (jacket) and lower garment (trousers)
form a matching business/formal suit.
Executed strictly post-item-classification.
"""

from typing import List, Dict, Any, Tuple
from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService
import logging

logger = logging.getLogger(__name__)

class SuitDetector:
    @staticmethod
    def detect_suit(items: List[Dict[str, Any]], vlm_outfit_context: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Determines whether upper and lower items form a matching suit.
        Returns (is_suit: bool, confidence: float).
        """
        upper_item = None
        lower_item = None
        footwear_item = None

        for it in items:
            cat = it.get("category", "")
            itype = it.get("item_type", "")
            if isinstance(itype, dict):
                itype = itype.get("value", "")
            itype = ItemTaxonomyService.normalize_item_type(itype)

            if cat == "upper_body" or itype in ["suit_jacket", "blazer", "casual_jacket", "casual_shirt", "dress_shirt"]:
                if not upper_item:
                    upper_item = it
            elif cat == "lower_body" or itype in ["suit_trousers", "formal_trousers", "loose_pants", "jeans", "chinos"]:
                if not lower_item:
                    lower_item = it
            elif cat == "footwear":
                footwear_item = it

        if not upper_item or not lower_item:
            return False, 0.0

        upper_type = upper_item.get("item_type", "")
        if isinstance(upper_type, dict):
            upper_type = upper_type.get("value", "")

        lower_type = lower_item.get("item_type", "")
        if isinstance(lower_type, dict):
            lower_type = lower_type.get("value", "")

        # EXPLICIT RULE 1: Sandals / Slides / Sneakers / Jeans / Shorts / Joggers NEVER form a suit
        footwear_type = footwear_item.get("item_type", "") if footwear_item else ""
        if isinstance(footwear_type, dict):
            footwear_type = footwear_type.get("value", "")
        
        if footwear_type in ["sandals", "slides", "flip_flops", "sneakers"] or lower_type in ["jeans", "shorts", "joggers", "cargo_pants"]:
            return False, 0.95

        upper_color = upper_item.get("color", {}).get("primary", "") if isinstance(upper_item.get("color"), dict) else upper_item.get("primary_color", "")
        lower_color = lower_item.get("color", {}).get("primary", "") if isinstance(lower_item.get("color"), dict) else lower_item.get("primary_color", "")

        formal_colors = ["navy", "black", "charcoal", "dark grey", "grey", "dark navy"]

        # Check for matching dark suit jacket + trousers + formal shoes
        has_tie = any(it.get("category") == "accessory" or it.get("item_type") == "tie" or (isinstance(it.get("item_type"), dict) and it.get("item_type", {}).get("value") == "tie") for it in items)

        if upper_color in formal_colors and lower_color in formal_colors and (upper_color == lower_color or (upper_color in ["navy", "black"] and lower_color in ["navy", "black"])):
            if has_tie or footwear_type in ["formal_shoes", "oxford_shoes", "derby_shoes"]:
                # Refine upper and lower item types if needed
                upper_item["item_type"] = {"value": "suit_jacket", "confidence": 0.95}
                upper_item["category"] = "upper_body"
                upper_item["display_name"] = "Suit Jacket"
                
                lower_item["item_type"] = {"value": "suit_trousers", "confidence": 0.95}
                lower_item["category"] = "lower_body"
                lower_item["display_name"] = "Suit Trousers"
                
                return True, 0.95

        return False, 0.80

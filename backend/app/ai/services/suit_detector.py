"""
Suit Detector — Relationship Analyzer for Suit Matching.

Evaluates whether detected upper garment (jacket) and lower garment (trousers)
form a matching formal suit relationship.
Operates post-classification WITHOUT mutating underlying detected item instances.
"""

from typing import List, Dict, Any, Tuple
from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService
import logging

logger = logging.getLogger(__name__)

class SuitDetector:
    @staticmethod
    def detect_suit(items: List[Dict[str, Any]], vlm_outfit_context: Dict[str, Any] = None) -> Tuple[bool, float, List[str]]:
        """
        Determines whether upper and lower items form a matching suit.
        Returns (is_suit: bool, confidence: float, matched_region_ids: List[str]).
        NEVER mutates item classifications directly inside suit detector.
        """
        upper_item = None
        lower_item = None
        footwear_item = None

        for it in items:
            cat_group = it.get("category_group", "")
            itype = it.get("item_type", "")
            if isinstance(itype, dict):
                itype = itype.get("value", "")
            itype = ItemTaxonomyService.normalize_item_type(itype)

            if cat_group in ["upper_body", "outerwear"] or itype in ["suit_jacket", "blazer"]:
                if not upper_item:
                    upper_item = it
            elif cat_group == "lower_body" or itype in ["suit_trousers", "formal_trousers"]:
                if not lower_item:
                    lower_item = it
            elif cat_group == "footwear":
                footwear_item = it

        if not upper_item or not lower_item:
            return False, 0.0, []

        upper_type = upper_item.get("item_type", "")
        if isinstance(upper_type, dict):
            upper_type = upper_type.get("value", "")
        upper_type = ItemTaxonomyService.normalize_item_type(upper_type)

        lower_type = lower_item.get("item_type", "")
        if isinstance(lower_type, dict):
            lower_type = lower_type.get("value", "")
        lower_type = ItemTaxonomyService.normalize_item_type(lower_type)

        # Exclusion Rule: Sandals, slides, sneakers, jeans, shorts NEVER form a suit
        footwear_type = footwear_item.get("item_type", "") if footwear_item else ""
        if isinstance(footwear_type, dict):
            footwear_type = footwear_type.get("value", "")
        footwear_type = ItemTaxonomyService.normalize_item_type(footwear_type)
        
        if footwear_type in ["sandals", "slides", "flip_flops", "sneakers"] or lower_type in ["jeans", "shorts", "joggers"]:
            return False, 0.95, []

        upper_color = upper_item.get("color", {}).get("primary", "") if isinstance(upper_item.get("color"), dict) else upper_item.get("primary_color", "")
        lower_color = lower_item.get("color", {}).get("primary", "") if isinstance(lower_item.get("color"), dict) else lower_item.get("primary_color", "")

        formal_colors = ["navy", "black", "charcoal", "dark grey", "grey"]

        # Require matching suit_jacket + suit_trousers categories or compatible formal colors + formal shoes/tie
        if upper_type in ["suit_jacket", "blazer"] and lower_type in ["suit_trousers", "formal_trousers"]:
            if upper_color in formal_colors and lower_color in formal_colors and upper_color == lower_color:
                matched_ids = [upper_item.get("region_id", ""), lower_item.get("region_id", "")]
                return True, 0.92, matched_ids

        return False, 0.80, []

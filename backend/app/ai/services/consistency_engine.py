"""
Consistency Engine — Contradiction Detection and Attribute Dependency Enforcement.

Validates item predictions and overall outfit context against consistency rules
and taxonomy constraints. Corrects invalid state or flags needs_confirmation.
"""

from typing import Dict, Any, List
from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService
import logging

logger = logging.getLogger(__name__)

class ConsistencyEngine:
    @staticmethod
    def validate_and_correct_item(item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforces item_type as the SINGLE SOURCE OF TRUTH for category and display_name.
        Validates attribute dependencies and formality consistency.
        """
        raw_type = item.get("item_type", "casual_shirt")
        if isinstance(raw_type, dict):
            raw_type = raw_type.get("value", "casual_shirt")

        canonical_type = ItemTaxonomyService.normalize_item_type(str(raw_type))
        entry = ItemTaxonomyService.get_entry(canonical_type)

        # Force structural dependency: item_type -> category & display_name
        item["item_type"] = {"value": canonical_type, "confidence": item.get("confidence", 0.90)}
        item["category"] = entry.category
        item["display_name"] = entry.display_name

        # Validate formality range vs item_type
        formality_val = item.get("formality", {}).get("value", entry.base_formality) if isinstance(item.get("formality"), dict) else entry.base_formality
        
        needs_confirm = item.get("needs_confirmation", False)

        if canonical_type in ["sandals", "slides"] and formality_val > 4:
            formality_val = 2
            needs_confirm = True
        elif canonical_type in ["suit_jacket", "suit_trousers"] and formality_val < 7:
            formality_val = 9
            needs_confirm = True
        elif canonical_type in ["t_shirt", "joggers", "shorts"] and formality_val > 5:
            formality_val = 2
            needs_confirm = True

        item["formality"] = {"value": int(formality_val), "confidence": 0.90}
        item["needs_confirmation"] = needs_confirm

        return item

    @staticmethod
    def validate_outfit_consistency(overall_outfit: Dict[str, Any], items: List[Dict[str, Any]], is_suit: bool) -> Dict[str, Any]:
        """Validates overall outfit style and formality for contradictions."""
        style = overall_outfit.get("style", "casual")
        formality = overall_outfit.get("formality", 3)

        footwear_types = []
        item_types = []
        for it in items:
            itype = it.get("item_type", {}).get("value", "") if isinstance(it.get("item_type"), dict) else it.get("item_type", "")
            itype_canonical = ItemTaxonomyService.normalize_item_type(itype)
            item_types.append(itype_canonical)
            if ItemTaxonomyService.derive_category(itype_canonical) == "footwear":
                footwear_types.append(itype_canonical)

        # Rule: Sandals / Slides cannot be Business Formal
        if any(f in ["sandals", "slides"] for f in footwear_types) and style in ["business formal", "formal"]:
            overall_outfit["style"] = "casual"
            overall_outfit["formality"] = 3

        # Rule: Suit without casual elements must be Formal/Business Formal
        if is_suit and not any(f in ["sandals", "slides"] for f in footwear_types):
            overall_outfit["style"] = "business formal"
            overall_outfit["formality"] = 9

        return overall_outfit

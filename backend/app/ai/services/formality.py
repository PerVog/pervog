"""
Formality Calculation Engine.

Programmatically computes item and outfit formality scores based on item types,
footwear, outfit context, materials, and suit relationships dynamically.
"""

from typing import Dict, Any, List, Optional
from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService
from app.ai.models.schemas import FormalityScoreDetail
import logging

logger = logging.getLogger(__name__)

class FormalityService:
    @staticmethod
    def calculate_item_formality(item_type: str, footwear_type: str = "", is_suit: bool = False, has_tie: bool = False) -> FormalityScoreDetail:
        """Calculates dynamic item formality score (1 to 10)."""
        entry = ItemTaxonomyService.get_entry(item_type)
        score = float(entry.base_formality)

        # Dynamic Suit Relationship Bonus
        if is_suit and item_type in ["suit_jacket", "suit_trousers"]:
            score = max(score, 9.0)
            if has_tie:
                score += 0.5

        # Footwear context adjustment
        if footwear_type in ["sandals", "slides", "flip_flops"]:
            score = max(1.0, score - 3.0)
        elif footwear_type in ["sneakers", "running_shoes"]:
            score = max(1.0, score - 2.0)
        elif footwear_type in ["formal_shoes", "oxford_shoes", "derby_shoes"] and is_suit:
            score = min(10.0, score + 0.5)

        final_val = int(round(max(1.0, min(10.0, score))))
        return FormalityScoreDetail(value=final_val, confidence=0.90)

    @staticmethod
    def calculate_outfit_formality(items: List[Dict[str, Any]], is_suit: bool = False) -> Dict[str, Any]:
        """Calculates overall outfit formality and style category dynamically."""
        if not items:
            return {"formality": None, "style": "unknown", "confidence": 0.80}

        item_types = []
        footwear_type = ""
        for it in items:
            itype = it.get("item_type", "")
            if isinstance(itype, dict):
                itype = itype.get("value", "")
            itype_canonical = ItemTaxonomyService.normalize_item_type(itype)
            item_types.append(itype_canonical)

            if ItemTaxonomyService.derive_category(itype_canonical) == "footwear":
                footwear_type = itype_canonical

        has_sandals_or_slides = footwear_type in ["sandals", "slides"]
        has_casual_garment = any(t in ["t_shirt", "hoodie", "shorts", "loose_pants", "cargo_pants", "casual_shirt"] for t in item_types)

        if is_suit and not has_sandals_or_slides:
            formality_score = 9
            if footwear_type in ["formal_shoes", "oxford_shoes", "derby_shoes"]:
                formality_score = 10
            return {"formality": formality_score, "style": "business formal", "confidence": 0.95}

        # Rule: Sandals / Slides or Casual Shirt + Loose Pants -> Casual
        if has_sandals_or_slides or ("casual_shirt" in item_types and "loose_pants" in item_types):
            return {"formality": 3, "style": "casual", "confidence": 0.92}

        if has_casual_garment and "suit_jacket" not in item_types and "blazer" not in item_types:
            return {"formality": 3, "style": "casual", "confidence": 0.90}

        if "blazer" in item_types or "dress_shirt" in item_types or "formal_trousers" in item_types or "chinos" in item_types:
            if footwear_type in ["sneakers", "loafers"]:
                return {"formality": 6, "style": "smart casual", "confidence": 0.88}
            return {"formality": 7, "style": "smart casual", "confidence": 0.88}

        return {"formality": 4, "style": "casual", "confidence": 0.85}

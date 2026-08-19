"""
Formality Calculation Engine.

Programmatically computes item and outfit formality scores based on item types,
footwear, outfit context, materials, and suit relationships dynamically.
Exposes reasoning string for score verification.
"""

from typing import Dict, Any, List, Optional
from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService
from app.ai.models.schemas import FormalityScoreDetail
import logging

logger = logging.getLogger(__name__)

class FormalityService:
    @staticmethod
    def calculate_item_formality(item_type: str, footwear_type: str = "", is_suit: bool = False, has_tie: bool = False) -> FormalityScoreDetail:
        """Calculates dynamic item formality score (1 to 10) with reasoning."""
        entry = ItemTaxonomyService.get_entry(item_type)
        score = float(entry.base_formality)
        reasons = [f"Base formality for {entry.display_name}: {entry.base_formality}"]

        if is_suit and item_type in ["suit_jacket", "suit_trousers"]:
            score = max(score, 9.0)
            reasons.append("Suit relationship match: set to >= 9.0")
            if has_tie:
                score += 0.5
                reasons.append("Matching tie: +0.5")

        if footwear_type in ["sandals", "slides"]:
            score = max(1.0, score - 3.0)
            reasons.append("Casual footwear context (sandals/slides): -3.0")
        elif footwear_type in ["sneakers", "running_shoes"]:
            score = max(1.0, score - 2.0)
            reasons.append("Athletic footwear context: -2.0")

        final_val = int(round(max(1.0, min(10.0, score))))
        reasoning_str = "; ".join(reasons)
        return FormalityScoreDetail(value=final_val, confidence=0.90, reasoning=reasoning_str)

    @staticmethod
    def calculate_outfit_formality(items: List[Dict[str, Any]], is_suit: bool = False) -> Dict[str, Any]:
        """Calculates overall outfit formality and style category dynamically."""
        if not items:
            return {"formality": 3, "style": "casual", "confidence": 0.50}

        item_types = []
        footwear_type = ""
        for it in items:
            itype = it.get("item_type", "")
            if isinstance(itype, dict):
                itype = itype.get("value", "")
            itype_canonical = ItemTaxonomyService.normalize_item_type(itype)
            item_types.append(itype_canonical)

            if ItemTaxonomyService.derive_category_group(itype_canonical) == "footwear":
                footwear_type = itype_canonical

        has_sandals = footwear_type in ["sandals", "slides"]
        has_casual = any(t in ["t_shirt", "hoodie", "shorts", "loose_pants", "cargo_pants"] for t in item_types)

        if is_suit and not has_sandals:
            return {"formality": 9, "style": "business formal", "confidence": 0.95}

        if has_sandals:
            return {"formality": 2, "style": "casual", "confidence": 0.92}

        if has_casual and "suit_jacket" not in item_types and "blazer" not in item_types:
            return {"formality": 3, "style": "casual", "confidence": 0.90}

        if "blazer" in item_types or "dress_shirt" in item_types or "formal_trousers" in item_types:
            if footwear_type in ["sneakers", "loafers"]:
                return {"formality": 6, "style": "smart casual", "confidence": 0.88}
            return {"formality": 7, "style": "smart casual", "confidence": 0.88}

        return {"formality": 4, "style": "casual", "confidence": 0.85}

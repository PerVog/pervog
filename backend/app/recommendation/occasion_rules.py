from typing import Dict, Tuple

OCCASION_FORMALITY_MAP: Dict[str, Tuple[int, int]] = {
    "college": (2, 5),
    "office": (6, 8),
    "interview": (8, 10),
    "casual outing": (2, 5),
    "casual": (2, 5),
    "date": (5, 8),
    "party": (4, 7),
    "wedding": (7, 10),
    "travel": (1, 4),
    "gym": (1, 3),
    "sports": (1, 3),
    "beach": (1, 3),
    "dinner": (5, 8),
    "formal event": (8, 10),
    "traditional event": (5, 9),
}

class OccasionService:
    @staticmethod
    def get_preferred_formality(occasion_name: str) -> Tuple[int, int]:
        occ_clean = occasion_name.lower().strip()
        for key, range_val in OCCASION_FORMALITY_MAP.items():
            if key in occ_clean or occ_clean in key:
                return range_val
        return (2, 6) # Default casual-to-smart-casual

    @staticmethod
    def score_item_for_occasion(item_formality: int, item_occasions: list, target_occasion: str) -> float:
        min_f, max_f = OccasionService.get_preferred_formality(target_occasion)
        
        # Formality fit score
        if min_f <= item_formality <= max_f:
            formality_score = 100.0
        else:
            diff = min(abs(item_formality - min_f), abs(item_formality - max_f))
            formality_score = max(20.0, 100.0 - (diff * 25.0))

        # Explicit occasion tag match bonus
        target_clean = target_occasion.lower().strip()
        has_tag_match = any(target_clean in tag.lower() or tag.lower() in target_clean for tag in (item_occasions or []))
        tag_bonus = 10.0 if has_tag_match else 0.0

        return min(100.0, formality_score + tag_bonus)

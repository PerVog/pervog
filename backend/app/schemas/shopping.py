from pydantic import BaseModel
from typing import List

class ShoppingGapRecommendation(BaseModel):
    category: str
    suggested_item: str
    color: str
    reason: str
    compatible_tops_count: int
    compatible_bottoms_count: int
    potential_outfits_unlocked: int
    usefulness_score: str # HIGH, MEDIUM, EXCELLENT

class ShoppingGapResponse(BaseModel):
    user_id: int
    total_wardrobe_count: int
    missing_gaps: List[ShoppingGapRecommendation]

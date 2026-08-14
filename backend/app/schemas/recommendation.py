from pydantic import BaseModel
from typing import Optional, List, Dict
from app.schemas.wardrobe import WardrobeItemResponse

class RecommendationRequest(BaseModel):
    user_id: int
    occasion: str = "Casual Outing"
    location: Optional[str] = None
    use_current_weather: bool = True
    manual_temperature_c: Optional[float] = None
    manual_rain: Optional[bool] = None
    style_preference_override: Optional[str] = None
    selected_item_id: Optional[int] = None
    limit: int = 5

class OutfitItemDetail(BaseModel):
    role: str # top, bottom, footwear, jacket, accessory
    item: WardrobeItemResponse

class OutfitRecommendationResponse(BaseModel):
    id: Optional[int] = None
    title: str
    occasion: str
    weather_condition: Optional[str] = None
    temperature_c: Optional[float] = None
    score: float
    score_breakdown: Dict[str, float]
    reasons: List[str]
    items: List[OutfitItemDetail]
    is_saved: bool = False

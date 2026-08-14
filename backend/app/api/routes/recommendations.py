from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.recommendation import RecommendationRequest, OutfitRecommendationResponse
from app.services.user_service import UserService
from app.services.wardrobe_service import WardrobeService
from app.services.user_preference_service import UserPreferenceService
from app.weather.weather_service import WeatherService
from app.recommendation.engine import RecommendationEngine

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.post("", response_model=List[OutfitRecommendationResponse])
def get_recommendations(req: RecommendationRequest, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_user_by_id(req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    wardrobe_service = WardrobeService(db)
    wardrobe_items = wardrobe_service.get_user_items(user_id=req.user_id)

    if not wardrobe_items:
        raise HTTPException(status_code=400, detail="Wardrobe is empty. Upload items to get outfit recommendations.")

    # Get weather
    location = req.location or (user.profile.location if user.profile else "New York")
    weather_service = WeatherService(db)
    weather_info = weather_service.get_weather(location)

    temp_c = req.manual_temperature_c if req.manual_temperature_c is not None else weather_info.temperature_c
    rain_prob = 80 if req.manual_rain else weather_info.rain_probability

    # Get user affinity from feedback
    pref_service = UserPreferenceService(db)
    user_affinity = pref_service.get_user_affinity(req.user_id)

    profile_dict = {
        "preferred_fit": user.profile.preferred_fit if user.profile else "regular",
        "favorite_colors": user.profile.favorite_colors if user.profile else [],
        "disliked_colors": user.profile.disliked_colors if user.profile else [],
        "preferred_styles": user.profile.preferred_styles if user.profile else ["casual"],
    }

    context = {
        "occasion": req.occasion,
        "temperature_c": temp_c,
        "rain_probability": rain_prob,
        "weather_condition": weather_info.weather_condition,
        "profile": profile_dict,
        "user_affinity": user_affinity
    }

    engine = RecommendationEngine()
    outfits = engine.generate_recommendations(
        wardrobe_items=wardrobe_items,
        context=context,
        selected_item_id=req.selected_item_id,
        limit=req.limit
    )

    return outfits

@router.post("/item/{item_id}", response_model=List[OutfitRecommendationResponse])
def recommend_for_item(
    item_id: int,
    user_id: int = 1,
    occasion: str = "Casual Outing",
    db: Session = Depends(get_db)
):
    req = RecommendationRequest(
        user_id=user_id,
        occasion=occasion,
        selected_item_id=item_id,
        limit=5
    )
    return get_recommendations(req, db)

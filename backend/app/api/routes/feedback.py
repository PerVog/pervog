from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.schemas.recommendation import OutfitRecommendationResponse
from app.services.user_preference_service import UserPreferenceService
from app.models.outfit import Outfit

router = APIRouter(prefix="/outfits", tags=["Outfits & Feedback"])

@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(data: FeedbackCreate, db: Session = Depends(get_db)):
    service = UserPreferenceService(db)
    return service.record_feedback(data)

@router.get("/saved", response_model=List[OutfitRecommendationResponse])
def get_saved_outfits(user_id: int = 1, db: Session = Depends(get_db)):
    saved_outfits = db.query(Outfit).filter(Outfit.user_id == user_id, Outfit.is_saved == True).all()
    res = []
    for o in saved_outfits:
        items = []
        for it_rel in o.items:
            items.append({
                "role": it_rel.role,
                "item": it_rel.item
            })
        res.append({
            "id": o.id,
            "title": o.title,
            "occasion": o.occasion,
            "weather_condition": o.weather_condition,
            "temperature_c": o.temperature_c,
            "score": o.score,
            "score_breakdown": o.score_breakdown or {},
            "reasons": o.reasons or [],
            "items": items,
            "is_saved": True
        })
    return res

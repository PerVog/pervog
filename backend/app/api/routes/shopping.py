from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.shopping import ShoppingGapResponse
from app.services.shopping_service import ShoppingService

router = APIRouter(prefix="/shopping", tags=["Shopping & Wardrobe Gaps"])

@router.get("/recommendations", response_model=ShoppingGapResponse)
def get_shopping_recommendations(user_id: int = 1, db: Session = Depends(get_db)):
    service = ShoppingService(db)
    return service.analyze_wardrobe_gaps(user_id)

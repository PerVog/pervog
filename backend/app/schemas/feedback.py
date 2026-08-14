from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FeedbackCreate(BaseModel):
    user_id: int
    outfit_id: int
    liked: Optional[bool] = None
    saved: Optional[bool] = None
    worn: Optional[bool] = None
    rating: Optional[int] = None

class FeedbackResponse(FeedbackCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

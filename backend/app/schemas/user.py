from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserProfileBase(BaseModel):
    age: Optional[int] = None
    gender_preference: Optional[str] = "all"
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    skin_tone: Optional[str] = "medium"
    preferred_fit: Optional[str] = "regular"
    preferred_styles: Optional[List[str]] = []
    favorite_colors: Optional[List[str]] = []
    disliked_colors: Optional[List[str]] = []
    favorite_brands: Optional[List[str]] = []
    location: Optional[str] = "New York"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    email: Optional[str] = None
    profile: Optional[UserProfileCreate] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    created_at: datetime
    profile: Optional[UserProfileResponse] = None

    class Config:
        from_attributes = True

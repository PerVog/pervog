from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WardrobeAttributeBase(BaseModel):
    subcategory: Optional[str] = None
    primary_color: str = "white"
    secondary_colors: Optional[List[str]] = []
    color_hex: Optional[str] = "#FFFFFF"
    pattern: Optional[str] = "solid"
    material: Optional[str] = "cotton"
    fit: Optional[str] = "regular"
    style: Optional[str] = "casual"
    formality: Optional[int] = 3
    seasons: Optional[List[str]] = ["spring", "summer", "autumn", "winter"]
    warmth: Optional[int] = 1
    occasions: Optional[List[str]] = ["casual", "college", "outing"]
    sleeve_type: Optional[str] = None
    condition: Optional[str] = "good"

class WardrobeAttributeCreate(WardrobeAttributeBase):
    pass

class WardrobeAttributeResponse(WardrobeAttributeBase):
    id: int
    item_id: int

    class Config:
        from_attributes = True

class WardrobeItemBase(BaseModel):
    title: str
    category: str
    image_url: str
    is_favorite: Optional[bool] = False
    is_available: Optional[bool] = True

class WardrobeItemCreate(WardrobeItemBase):
    attributes: Optional[WardrobeAttributeCreate] = None

class WardrobeItemUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_favorite: Optional[bool] = None
    is_available: Optional[bool] = None
    attributes: Optional[WardrobeAttributeCreate] = None

class WardrobeItemResponse(WardrobeItemBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    attributes: Optional[WardrobeAttributeResponse] = None

    class Config:
        from_attributes = True

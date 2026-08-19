import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.schemas.wardrobe import WardrobeItemCreate, WardrobeItemUpdate, WardrobeItemResponse
from app.services.wardrobe_service import WardrobeService
from app.storage.local_storage import LocalStorageProvider
from app.ai.clothing_analyzer import ClothingAnalyzer

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])
storage = LocalStorageProvider()
analyzer = ClothingAnalyzer()

@router.get("", response_model=List[WardrobeItemResponse])
def get_wardrobe(
    user_id: int = 1,
    category: Optional[str] = None,
    search: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    is_available: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    service = WardrobeService(db)
    return service.get_user_items(
        user_id=user_id,
        category=category,
        search=search,
        is_favorite=is_favorite,
        is_available=is_available
    )

@router.post("", response_model=WardrobeItemResponse)
def create_wardrobe_item(
    item_in: WardrobeItemCreate,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    service = WardrobeService(db)
    return service.create_item(user_id, item_in)

@router.post("/batch", response_model=List[WardrobeItemResponse])
def create_batch_wardrobe_items(
    items_in: List[WardrobeItemCreate],
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    service = WardrobeService(db)
    return service.create_batch_items(user_id, items_in)

@router.post("/upload")
def upload_clothing_image(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        fname = file.filename or "uploaded_image.jpg"
        url = storage.save_file(contents, fname)
        return {"image_url": url, "filename": fname}
    except Exception as e:
        logger.error(f"Image upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

@router.post("/analyze")
def analyze_uploaded_image(image_url: str):
    try:
        # Support full URLs (e.g. http://localhost:8000/uploads/xyz.jpg) and relative paths (/uploads/xyz.jpg)
        local_path = image_url
        if "/uploads/" in image_url:
            filename = image_url.split("/uploads/")[-1]
            local_path = os.path.join(storage.upload_dir, filename)
        
        analyzer = ClothingAnalyzer()
        analysis = analyzer.analyze(local_path)
        return {"image_url": image_url, **analysis}
    except Exception as e:
        logger.error(f"Image analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@router.get("/{item_id}", response_model=WardrobeItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    service = WardrobeService(db)
    item = service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Wardrobe item not found")
    return item

@router.put("/{item_id}", response_model=WardrobeItemResponse)
def update_item(item_id: int, item_in: WardrobeItemUpdate, db: Session = Depends(get_db)):
    service = WardrobeService(db)
    item = service.update_item(item_id, item_in)
    if not item:
        raise HTTPException(status_code=404, detail="Wardrobe item not found")
    return item

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    service = WardrobeService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Wardrobe item not found")
    return {"message": "Item deleted successfully"}

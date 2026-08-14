from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserProfileCreate, UserProfileResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model=UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_user(user_in)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}/profile", response_model=UserProfileResponse)
def update_profile(user_id: int, profile_in: UserProfileCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    profile = service.update_user_profile(user_id, profile_in)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile

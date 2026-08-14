from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserProfile
from app.schemas.user import UserCreate, UserProfileCreate

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_default_user(self) -> User:
        user = self.get_user_by_id(1)
        if not user:
            user = self.create_user(UserCreate(name="Alex Stylist", email="alex@example.com"))
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, data: UserCreate) -> User:
        user = User(name=data.name, email=data.email)
        self.db.add(user)
        self.db.flush()

        prof_data = data.profile or UserProfileCreate()
        profile = UserProfile(
            user_id=user.id,
            age=prof_data.age,
            gender_preference=prof_data.gender_preference or "all",
            height_cm=prof_data.height_cm,
            weight_kg=prof_data.weight_kg,
            skin_tone=prof_data.skin_tone or "medium",
            preferred_fit=prof_data.preferred_fit or "regular",
            preferred_styles=prof_data.preferred_styles or ["casual", "minimalist"],
            favorite_colors=prof_data.favorite_colors or ["white", "blue", "black"],
            disliked_colors=prof_data.disliked_colors or [],
            favorite_brands=prof_data.favorite_brands or [],
            location=prof_data.location or "New York",
            latitude=prof_data.latitude,
            longitude=prof_data.longitude
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user_profile(self, user_id: int, prof_data: UserProfileCreate) -> Optional[UserProfile]:
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)

        for field, val in prof_data.model_dump(exclude_unset=True).items():
            setattr(profile, field, val)

        self.db.commit()
        self.db.refresh(profile)
        return profile

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    wardrobe_items = relationship("WardrobeItem", back_populates="user", cascade="all, delete-orphan")
    outfits = relationship("Outfit", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("OutfitFeedback", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer, nullable=True)
    gender_preference = Column(String, nullable=True, default="all") # male, female, unisex, all
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    skin_tone = Column(String, nullable=True) # fair, medium, olive, dark, warm, cool
    preferred_fit = Column(String, nullable=True, default="regular") # slim, regular, relaxed, oversized
    preferred_styles = Column(JSON, default=list) # ["casual", "minimalist", "streetwear"]
    favorite_colors = Column(JSON, default=list) # ["white", "blue", "black"]
    disliked_colors = Column(JSON, default=list) # ["neon green", "magenta"]
    favorite_brands = Column(JSON, default=list)
    location = Column(String, nullable=True, default="New York")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")

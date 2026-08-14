from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False, default="Generated Outfit")
    occasion = Column(String, nullable=False, default="Casual")
    weather_condition = Column(String, nullable=True)
    temperature_c = Column(Float, nullable=True)
    score = Column(Float, nullable=False, default=80.0)
    score_breakdown = Column(JSON, default=dict) # {"color": 90, "occasion": 85, ...}
    reasons = Column(JSON, default=list) # ["✓ Strong color combination", ...]
    is_saved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="outfits")
    items = relationship("OutfitItem", back_populates="outfit", cascade="all, delete-orphan")
    feedbacks = relationship("OutfitFeedback", back_populates="outfit", cascade="all, delete-orphan")

class OutfitItem(Base):
    __tablename__ = "outfit_items"

    id = Column(Integer, primary_key=True, index=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("wardrobe_items.id"), nullable=False)
    role = Column(String, nullable=False) # top, bottom, footwear, jacket, accessory

    outfit = relationship("Outfit", back_populates="items")
    item = relationship("WardrobeItem", back_populates="outfit_items")

class OutfitFeedback(Base):
    __tablename__ = "outfit_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    liked = Column(Boolean, nullable=True) # True=like, False=dislike
    saved = Column(Boolean, default=False)
    worn = Column(Boolean, default=False)
    rating = Column(Integer, nullable=True) # 1 to 5
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedbacks")
    outfit = relationship("Outfit", back_populates="feedbacks")

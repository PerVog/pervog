from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False) # Top, Bottom, Footwear, Outerwear, Accessory, etc.
    image_url = Column(String, nullable=False)
    is_favorite = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="wardrobe_items")
    attributes = relationship("WardrobeItemAttribute", back_populates="item", uselist=False, cascade="all, delete-orphan")
    outfit_items = relationship("OutfitItem", back_populates="item", cascade="all, delete-orphan")

class WardrobeItemAttribute(Base):
    __tablename__ = "wardrobe_item_attributes"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("wardrobe_items.id"), unique=True, nullable=False)
    subcategory = Column(String, nullable=True) # e.g. casual shirt, chino, oxford shoes
    primary_color = Column(String, nullable=False, default="white")
    secondary_colors = Column(JSON, default=list) # e.g. ["blue", "grey"]
    color_hex = Column(String, nullable=True) # e.g. "#FFFFFF"
    pattern = Column(String, default="solid") # solid, striped, plaid, printed, etc.
    material = Column(String, default="cotton") # cotton, denim, leather, wool, linen, synthetic, suede
    fit = Column(String, default="regular") # slim, regular, relaxed, oversized
    style = Column(String, default="casual") # casual, formal, streetwear, athletic, traditional, smart_casual
    formality = Column(Integer, default=3) # 1 (very casual) to 10 (black tie formal)
    seasons = Column(JSON, default=lambda: ["spring", "summer", "autumn", "winter"]) # ["summer", "winter"]
    warmth = Column(Integer, default=1) # 1 (thin/breezy) to 5 (heavy coat)
    occasions = Column(JSON, default=lambda: ["casual", "college", "outing"]) # ["college", "party", "office"]
    sleeve_type = Column(String, nullable=True) # short, full, sleeveless, none
    condition = Column(String, default="good") # new, good, worn, fair

    item = relationship("WardrobeItem", back_populates="attributes")

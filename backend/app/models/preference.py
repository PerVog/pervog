from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    # Dynamic feature affinity weights (boost/penalty modifiers based on likes/dislikes)
    color_affinity = Column(JSON, default=dict) # {"white": +5, "red": -10}
    style_affinity = Column(JSON, default=dict) # {"casual": +3, "formal": -2}
    fit_affinity = Column(JSON, default=dict) # {"slim": +4}
    item_pair_affinity = Column(JSON, default=dict) # {"shirt_12+pants_4": +10}
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preferences")

from sqlalchemy.orm import Session
from app.models.outfit import Outfit, OutfitFeedback
from app.models.preference import UserPreference
from app.schemas.feedback import FeedbackCreate

class UserPreferenceService:
    def __init__(self, db: Session):
        self.db = db

    def record_feedback(self, data: FeedbackCreate) -> OutfitFeedback:
        feedback = OutfitFeedback(
            user_id=data.user_id,
            outfit_id=data.outfit_id,
            liked=data.liked,
            saved=data.saved or False,
            worn=data.worn or False,
            rating=data.rating
        )
        self.db.add(feedback)
        
        # If outfit saved, mark outfit as saved
        if data.saved:
            outfit = self.db.query(Outfit).filter(Outfit.id == data.outfit_id).first()
            if outfit:
                outfit.is_saved = True

        self.db.commit()
        self.db.refresh(feedback)

        # Update preference weights based on feedback
        self._update_user_preference_weights(data.user_id, data.outfit_id, data.liked, data.rating)

        return feedback

    def _update_user_preference_weights(self, user_id: int, outfit_id: int, liked: bool, rating: int):
        pref = self.db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        if not pref:
            pref = UserPreference(user_id=user_id, color_affinity={}, style_affinity={}, fit_affinity={}, item_pair_affinity={})
            self.db.add(pref)

        outfit = self.db.query(Outfit).filter(Outfit.id == outfit_id).first()
        if not outfit:
            return

        # Weight delta
        delta = 0
        if liked is True or (rating and rating >= 4):
            delta = 3
        elif liked is False or (rating and rating <= 2):
            delta = -5

        if delta == 0:
            return

        color_aff = dict(pref.color_affinity or {})
        for item_rel in outfit.items:
            item = item_rel.item
            if item and item.attributes:
                color = item.attributes.primary_color.lower() if item.attributes.primary_color else None
                if color:
                    color_aff[color] = color_aff.get(color, 0) + delta

        pref.color_affinity = color_aff
        self.db.commit()

    def get_user_affinity(self, user_id: int) -> dict:
        pref = self.db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        if not pref:
            return {"color_affinity": {}, "style_affinity": {}}
        return {
            "color_affinity": pref.color_affinity or {},
            "style_affinity": pref.style_affinity or {}
        }

from app.ai.config import ai_settings
from app.ai.models.schemas import AttributeValueWithConfidence

class AttributeNormalizer:
    @staticmethod
    def normalize_single(value: str, confidence: float) -> AttributeValueWithConfidence:
        conf = round(float(confidence), 2)
        needs_confirm = conf < ai_settings.CONFIDENCE_THRESHOLD
        return AttributeValueWithConfidence(
            value=value,
            confidence=conf,
            needs_confirmation=needs_confirm
        )

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AttributeValueWithConfidence(BaseModel):
    value: Any
    confidence: float = 0.85
    needs_confirmation: bool = False

class DominantColor(BaseModel):
    name: str
    rgb: List[int]
    percentage: float

class ColorDetailResult(BaseModel):
    primary: str
    secondary: List[str] = []
    dominant_colors: List[DominantColor] = []
    confidence: float = 0.85

class FormalityScoreDetail(BaseModel):
    value: int
    confidence: float = 0.85

class OverallOutfitContext(BaseModel):
    outfit_type: str = "single item"
    style: str = "casual"
    formality: int = 3
    occasion: List[str] = []
    confidence: float = 0.85

class CandidateHypothesis(BaseModel):
    type: str
    score: float

class PhysicalRegion(BaseModel):
    region_id: str
    bbox: List[int] = Field(default_factory=lambda: [0, 0, 100, 100])
    mask_path: Optional[str] = None
    crop_path: Optional[str] = None
    crop_hash: str = ""
    mask_area_ratio: float = 0.50
    candidate_types: List[CandidateHypothesis] = Field(default_factory=list)
    final_type: str = ""
    category_hint: str = ""
    models_detected: List[str] = Field(default_factory=list)
    model_evidence: Dict[str, Any] = Field(default_factory=dict)

class EvaluatedItemRegion(BaseModel):
    region_id: str
    bbox: List[int] = Field(default_factory=lambda: [0, 0, 100, 100])
    crop_hash: str = ""
    item_type: AttributeValueWithConfidence
    category: str
    display_name: str
    color: ColorDetailResult
    style: AttributeValueWithConfidence
    fit: AttributeValueWithConfidence
    material: AttributeValueWithConfidence
    formality: FormalityScoreDetail
    model_evidence: Dict[str, Any] = Field(default_factory=dict)
    needs_confirmation: bool = False
    
    # Backwards compatibility & Image URLs for UI rendering
    id: Optional[str] = None
    title: Optional[str] = None
    category_legacy: Optional[str] = None
    image_url: Optional[str] = None
    mask_url: Optional[str] = None
    suggested_metadata: Optional[Dict[str, Any]] = None

class FullClothingAnalysisResponse(BaseModel):
    success: bool = True
    overall_outfit: Optional[OverallOutfitContext] = None
    is_multi_item: bool = True
    is_suit: bool = False
    items: List[EvaluatedItemRegion] = []
    
    # Backwards compatibility top-level fallbacks for single item calls
    item_type: Optional[AttributeValueWithConfidence] = None
    category: Optional[AttributeValueWithConfidence] = None
    subcategory: Optional[AttributeValueWithConfidence] = None
    primary_color: Optional[AttributeValueWithConfidence] = None
    secondary_colors: List[AttributeValueWithConfidence] = []
    dominant_colors: List[DominantColor] = []
    pattern: Optional[AttributeValueWithConfidence] = None
    style: Optional[Any] = None
    fit: Optional[AttributeValueWithConfidence] = None
    material: Optional[AttributeValueWithConfidence] = None
    occasion: List[AttributeValueWithConfidence] = []
    season: List[str] = []
    weather: List[str] = []
    formality: Optional[FormalityScoreDetail] = None

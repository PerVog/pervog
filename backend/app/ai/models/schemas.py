"""
AI Vision Data Schemas — Multi-Model Data Flow Contracts.

Defines Pydantic data schemas for normalized detections, evidence separation,
physical regions, and clothing analysis API responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class NormalizedDetection(BaseModel):
    id: str
    source_model: str
    category_group: str          # upper_body, outerwear, lower_body, full_body, footwear, accessory
    garment_type: str            # tshirt, blazer, jeans, etc.
    physical_layer: str          # inner, outer, lower, full, footwear, accessory
    confidence: float
    bbox: List[int]              # [x1, y1, x2, y2]
    normalized_bbox: List[float] = Field(default_factory=list)
    person_id: Optional[str] = "person_001"
    mask: Optional[Any] = None
    label: str = ""

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
    source: Optional[str] = "mask_cielab_analysis"

class FormalityScoreDetail(BaseModel):
    value: int
    confidence: float = 0.85
    reasoning: Optional[str] = None

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
    person_id: Optional[str] = "person_001"
    category_group: str = "upper_body"
    garment_type: str = "unknown"
    physical_layer: str = "inner"
    bbox: List[int] = Field(default_factory=lambda: [0, 0, 100, 100])
    category_hint: str = ""
    candidate_labels: List[Dict[str, Any]] = Field(default_factory=list)
    models_detected: List[str] = Field(default_factory=list)
    fusion_score: float = 0.85
    provenance: Dict[str, Any] = Field(default_factory=dict)

class EvaluatedItemRegion(BaseModel):
    region_id: str
    person_id: Optional[str] = "person_001"
    category_group: str = "upper_body"
    garment_type: str = "casual_shirt"
    physical_layer: str = "inner"
    bbox: List[int] = Field(default_factory=lambda: [0, 0, 100, 100])
    crop_hash: str = ""
    item_type: AttributeValueWithConfidence
    category: str
    display_name: str
    color: ColorDetailResult
    color_hex: str = "#000000"
    style: AttributeValueWithConfidence
    fit: AttributeValueWithConfidence
    material: AttributeValueWithConfidence
    pattern: AttributeValueWithConfidence
    formality: FormalityScoreDetail
    confidence: float = 0.85
    needs_confirmation: bool = False

    # Evidence Separation Fields
    detection: Dict[str, Any] = Field(default_factory=dict)
    segmentation: Dict[str, Any] = Field(default_factory=dict)
    classification: Dict[str, Any] = Field(default_factory=dict)

    # Backwards compatibility & Image URLs for UI rendering
    id: Optional[str] = None
    title: Optional[str] = None
    crop_url: Optional[str] = None
    image_url: Optional[str] = None
    mask_url: Optional[str] = None
    model_evidence: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)

class PersonGroup(BaseModel):
    person_id: str
    bbox: List[int]
    garments: List[EvaluatedItemRegion] = []

class ClothingAnalysisResponse(BaseModel):
    success: bool = True
    overall_outfit: Optional[OverallOutfitContext] = None
    is_multi_item: bool = True
    is_suit: bool = False
    people: List[PersonGroup] = []
    items: List[EvaluatedItemRegion] = []
    
    # Provider diagnostic status
    provider_status: Dict[str, Any] = Field(default_factory=dict)

# Alias for API route compatibility
FullClothingAnalysisResponse = ClothingAnalysisResponse

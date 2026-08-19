"""
Ensemble Classifier — Multi-Model Evidence Voting & Evidence Preservation Engine.

Separates detection, classification, segmentation, and attribute evidence:
- Detection evidence (Grounding DINO, Florence-2, DeepFashion2) establishes physical object identity.
- Classification evidence (FashionCLIP) describes object type on crop.
- Failure of FashionCLIP/classifier NEVER erases valid detector evidence.
- NEVER defaults to 'casual_shirt' when evidence is missing.
"""

from typing import Dict, Any, List, Tuple
from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService
import numpy as np
import logging

logger = logging.getLogger(__name__)

SPECIFICITY_WEIGHTS = {
    "suit_jacket": 2.5,
    "blazer": 2.2,
    "dress_shirt": 2.2,
    "suit_trousers": 2.5,
    "formal_trousers": 2.2,
    "formal_shoes": 2.5,
    "oxford_shoes": 2.5,
    "derby_shoes": 2.5,
    "loafers": 2.2,
    "sandals": 2.5,
    "slides": 2.5,
    "running_shoes": 2.2,
    "sneakers": 2.0,
    "loose_pants": 2.2,
    "wide_leg_pants": 2.2,
    "jeans": 2.2,
    "chinos": 2.2,
    "hoodie": 2.2,
    "t_shirt": 2.0,
    "polo_shirt": 2.0,
    "casual_shirt": 1.5,
    "casual_jacket": 1.2
}

class EnsembleClassifier:
    def classify_region(
        self,
        region_id: str,
        category_hint: str,
        detector_candidate_labels: List[Any],
        fashionclip_rankings: List[Tuple[str, float]],
        vlm_analysis: Dict[str, Any],
        models_detected: List[str]
    ) -> Dict[str, Any]:
        """
        Calculates evidence scores for candidate item_types while preserving detector evidence.
        Returns explicit detection and classification evidence objects.
        """
        detector_scores: Dict[str, float] = {}
        model_evidence_log: Dict[str, Any] = {}

        # 1. Process Object Detector Labels (Grounding DINO, Florence-2, DeepFashion2)
        raw_labels = []
        for d_item in detector_candidate_labels:
            raw_lbl = d_item.get("raw_label", d_item.get("type", "unknown")) if isinstance(d_item, dict) else str(d_item)
            raw_labels.append(raw_lbl)
            canonical = ItemTaxonomyService.normalize_item_type(raw_lbl)
            weight = SPECIFICITY_WEIGHTS.get(canonical, 1.0)
            detector_scores[canonical] = detector_scores.get(canonical, 0.0) + weight

        model_evidence_log["detector_labels"] = {"labels": raw_labels, "models": models_detected}

        # Model Agreement Bonus
        if len(models_detected) >= 2:
            for canonical in list(detector_scores.keys()):
                detector_scores[canonical] += 1.5

        sorted_detectors = sorted(detector_scores.items(), key=lambda x: x[1], reverse=True)
        top_detector_type, top_detector_score = sorted_detectors[0] if sorted_detectors else ("unknown", 0.0)
        detection_confidence = round(min(0.98, max(0.0, top_detector_score / 6.0)), 2) if top_detector_type != "unknown" else 0.0

        detection_evidence = {
            "value": top_detector_type,
            "confidence": detection_confidence,
            "source": "detector_ensemble",
            "models_detected": models_detected
        }

        # 2. Process FashionCLIP crop candidate rankings
        classification_evidence = {
            "value": "unknown",
            "confidence": 0.0,
            "source": "none",
            "status": "unavailable"
        }

        top_clip_type = "unknown"
        top_clip_score = 0.0

        if fashionclip_rankings:
            top_clip_type, top_clip_score = fashionclip_rankings[0]
            top_clip_canonical = ItemTaxonomyService.normalize_item_type(top_clip_type)
            classification_evidence = {
                "value": top_clip_canonical,
                "confidence": round(float(top_clip_score), 4),
                "source": "fashion_clip",
                "status": "available"
            }
            model_evidence_log["fashionclip"] = {"top_candidate": top_clip_canonical, "score": round(top_clip_score, 4)}
        else:
            model_evidence_log["fashionclip"] = {"status": "unavailable"}

        # 3. Evidence Preservation Invariant:
        # If FashionCLIP fails/unavailable, RETAIN valid detector evidence.
        # If both fail, item_type = "unknown", confidence = 0.0.
        if classification_evidence["status"] == "available" and top_clip_score > 0.40:
            final_type = classification_evidence["value"]
            final_confidence = classification_evidence["confidence"]
        elif detection_evidence["value"] != "unknown":
            final_type = detection_evidence["value"]
            final_confidence = detection_evidence["confidence"]
            logger.info(f"Preserving detector evidence for {region_id}: {final_type} ({final_confidence})")
        else:
            final_type = "unknown"
            final_confidence = 0.0

        if final_type == "unknown":
            category_group = "unknown"
            garment_type = "unknown"
            physical_layer = "unknown"
            display_name = "Unknown Item"
            needs_confirmation = True
        else:
            entry = ItemTaxonomyService.get_entry(final_type)
            category_group = entry.category_group
            garment_type = entry.garment_type
            physical_layer = entry.physical_layer
            display_name = entry.display_name
            needs_confirmation = final_confidence < 0.35

        return {
            "item_type": final_type,
            "category_group": category_group,
            "garment_type": garment_type,
            "physical_layer": physical_layer,
            "category": ItemTaxonomyService.derive_category(final_type) if final_type != "unknown" else "unknown",
            "display_name": display_name,
            "confidence": final_confidence,
            "detection": detection_evidence,
            "classification": classification_evidence,
            "model_evidence": model_evidence_log,
            "needs_confirmation": needs_confirmation
        }

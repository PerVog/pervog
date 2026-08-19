"""
Ensemble Classifier — Multi-Model Evidence Voting and Calibrated Classification Engine.

Integrates evidence from Grounding DINO, Florence-2, DeepFashion2, FashionCLIP,
garment-attributes, and Qwen2.5-VL using a calibrated evidence weighting framework.
Calculates final item_type, category, display_name, confidence, candidate_margin, and needs_confirmation.
"""

from typing import Dict, Any, List, Tuple
from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Specificity weights for fashion item types
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
        Calculates evidence scores for candidate item_types and selects top candidate.
        Determines needs_confirmation using candidate_margin (< 0.10), confidence threshold, and model agreement.
        """
        evidence_scores: Dict[str, float] = {}
        model_evidence_log: Dict[str, Any] = {}

        # 1. Process FashionCLIP candidates
        top_clip_type, top_clip_score = fashionclip_rankings[0] if fashionclip_rankings else ("casual_shirt", 0.5)
        top_clip_canonical = ItemTaxonomyService.normalize_item_type(top_clip_type)
        clip_weight = SPECIFICITY_WEIGHTS.get(top_clip_canonical, 1.5)
        evidence_scores[top_clip_canonical] = evidence_scores.get(top_clip_canonical, 0.0) + (clip_weight * (1.5 if top_clip_score > 0.5 else 1.0))
        model_evidence_log["fashionclip"] = {"top_candidate": top_clip_canonical, "score": round(top_clip_score, 4)}

        # 2. Process Object Detector Labels (Grounding DINO & Florence-2)
        raw_labels = []
        for d_item in detector_candidate_labels:
            raw_lbl = d_item.get("raw_label", d_item.get("type", "clothing item")) if isinstance(d_item, dict) else str(d_item)
            raw_labels.append(raw_lbl)
            canonical = ItemTaxonomyService.normalize_item_type(raw_lbl)
            weight = SPECIFICITY_WEIGHTS.get(canonical, 1.0)
            evidence_scores[canonical] = evidence_scores.get(canonical, 0.0) + weight

        model_evidence_log["detector_labels"] = {"labels": raw_labels, "models": models_detected}

        # 3. Model Agreement Bonus
        if len(models_detected) >= 2:
            for canonical in list(evidence_scores.keys()):
                evidence_scores[canonical] += 1.5

        # 4. Process Qwen2.5-VL / VLM Evidence
        vlm_items = vlm_analysis.get("detected_items", [])
        vlm_matched = False
        vlm_top_type = None
        for item in vlm_items:
            raw_vlm_type = item.get("item_type", "")
            canonical_vlm = ItemTaxonomyService.normalize_item_type(raw_vlm_type)
            if ItemTaxonomyService.derive_category(canonical_vlm) == category_hint:
                weight = SPECIFICITY_WEIGHTS.get(canonical_vlm, 2.0)
                evidence_scores[canonical_vlm] = evidence_scores.get(canonical_vlm, 0.0) + weight
                vlm_top_type = canonical_vlm
                model_evidence_log["qwen"] = {"item_type": canonical_vlm, "agreement": True}
                vlm_matched = True
                break

        if not vlm_matched:
            model_evidence_log["qwen"] = {"agreement": False}

        # 5. Penalize Contradictory Types
        for candidate, score in list(evidence_scores.items()):
            candidate_cat = ItemTaxonomyService.derive_category(candidate)
            if candidate_cat != category_hint and category_hint in ["upper_body", "lower_body", "footwear"]:
                evidence_scores[candidate] -= 3.0

        # Select winner with highest evidence score
        sorted_candidates = sorted(evidence_scores.items(), key=lambda x: x[1], reverse=True)
        winning_type, winning_score = sorted_candidates[0] if sorted_candidates else ("casual_shirt", 1.0)
        
        # Softmax / Relative Margin Calculation (Refinement 5)
        total_score = sum(max(0.01, s) for _, s in sorted_candidates)
        top_prob = max(0.01, winning_score) / float(total_score)
        second_prob = (max(0.01, sorted_candidates[1][1]) / float(total_score)) if len(sorted_candidates) > 1 else 0.0
        candidate_margin = top_prob - second_prob

        # Enforce canonical taxonomy
        canonical_type = ItemTaxonomyService.normalize_item_type(winning_type)
        category = ItemTaxonomyService.derive_category(canonical_type)
        display_name = ItemTaxonomyService.derive_display_name(canonical_type)

        confidence = round(min(0.98, max(0.55, winning_score / 7.0)), 2)

        # Calibrated Candidate Margin (margin < 0.10 -> ambiguous -> needs_confirmation = True)
        model_disagreement = (vlm_top_type and vlm_top_type != canonical_type) or (top_clip_canonical != canonical_type)
        needs_confirmation = (confidence < 0.65) or (candidate_margin < 0.10) or model_disagreement

        model_evidence_log["candidate_margin"] = round(candidate_margin, 2)
        model_evidence_log["model_disagreement"] = model_disagreement

        return {
            "item_type": canonical_type,
            "category": category,
            "display_name": display_name,
            "confidence": confidence,
            "candidate_margin": round(candidate_margin, 2),
            "model_evidence": model_evidence_log,
            "needs_confirmation": needs_confirmation
        }

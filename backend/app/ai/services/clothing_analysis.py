"""
Clothing Analysis Service — Multi-Model Computer Vision Pipeline Orchestrator.

Implements full multi-stage architecture:
1. Multi-Model Detection (Grounding DINO, Florence-2, DeepFashion2)
2. Person Detection & Person ID Association (PersonDetector)
3. Single Normalized Detection Schema (category_group, garment_type, physical_layer)
4. Multi-Feature Physical Fusion & Layer Deduplication (PhysicalRegionFusionEngine)
5. SAM 2.1 Mask Segmentation
6. Adaptive Mask Quality Gate (MaskQualityChecker)
7. Pre-Classification Crop Quality Gate (CropQualityChecker)
8. FashionCLIP Zero-Shot Candidate Ranking (FashionCLIPProvider)
9. Mask-Only CIELAB Color Analysis (ColorAnalyzerService)
10. Suit Relationship & Outfit Reasoning (SuitDetector, FormalityService)
11. Pipeline Validation Gates (PipelineValidator)
12. Traceable Visual Debug Output (debug_runs/<timestamp>/)
"""

from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw
import numpy as np
import cv2
import os
import json
import uuid
from datetime import datetime
import logging

from app.ai.model_manager import ModelManager
from app.storage.storage_manager import StorageManager
from app.ai.providers.visual_embedding_provider import VisualEmbeddingProvider
from app.ai.services.person_detector import PersonDetector
from app.ai.services.physical_region_fusion import PhysicalRegionFusionEngine
from app.ai.services.mask_quality_checker import MaskQualityChecker
from app.ai.services.crop_quality_checker import CropQualityChecker
from app.ai.services.crop_validator import CropValidator
from app.ai.services.color_analysis import ColorAnalyzerService
from app.ai.services.ensemble_classifier import EnsembleClassifier
from app.ai.services.suit_detector import SuitDetector
from app.ai.services.formality import FormalityService
from app.ai.services.consistency_engine import ConsistencyEngine
from app.ai.services.fit_detector import FitDetector
from app.ai.services.pipeline_validator import PipelineValidator
from app.ai.taxonomy.item_taxonomy import ItemTaxonomyService
from app.ai.models.schemas import (
    FullClothingAnalysisResponse,
    EvaluatedItemRegion,
    OverallOutfitContext,
    AttributeValueWithConfidence,
    ColorDetailResult,
    FormalityScoreDetail,
    DominantColor,
    PersonGroup
)

logger = logging.getLogger(__name__)

class ClothingAnalysisService:
    def __init__(self):
        self.model_mgr = ModelManager()
        self.storage_mgr = StorageManager()
        self.visual_embedding_prov = VisualEmbeddingProvider()
        self.fusion_engine = PhysicalRegionFusionEngine()
        self.color_analyzer = ColorAnalyzerService()
        self.ensemble_classifier = EnsembleClassifier()

    def analyze(self, image: Image.Image) -> FullClothingAnalysisResponse:
        """Runs the complete multi-model computer vision pipeline on the image."""
        analysis_id = str(uuid.uuid4())[:8]

        image_rgb = image.convert("RGB")
        width, height = image_rgb.size
        image_np = np.array(image_rgb)

        # Stage 1: Gather Detections from Available Providers
        grounding_dets = self.model_mgr.grounding_dino.detect(image_rgb)
        florence_dets = self.model_mgr.florence.detect(image_rgb)
        deepfashion_dets = self.model_mgr.deepfashion2.detect(image_rgb)

        all_detections = grounding_dets + florence_dets + deepfashion_dets

        # Provider Diagnostics
        provider_status = self.model_mgr.get_provider_status()

        # Stage 2: Person Instance Detection
        people_instances = PersonDetector.extract_people(all_detections, width, height)

        # Stage 3: Physical Region Fusion & Layer Deduplication
        fused_regions, discarded_log = self.fusion_engine.fuse_detections(all_detections, width, height)

        # Qwen-VL Full Image Context
        vlm_analysis = self.model_mgr.qwen_vl.analyze_full_image(image_rgb)

        evaluated_items: List[Dict[str, Any]] = []
        crop_hashes_seen = set()
        debug_crops = []

        # Stage 4-8: Process each Fused Physical Garment Region
        for region in fused_regions:
            region_id = region["region_id"]
            person_id = region.get("person_id", "person_001")
            bbox = region["bbox"]
            category_group = region.get("category_group", "upper_body")

            # SAM 2.1 Mask Generation
            sam_result = self.model_mgr.sam2.generate_mask(image_rgb, bbox)
            mask = sam_result["mask"]
            crop = sam_result["crop"]

            # Adaptive Mask Quality Gate
            is_valid_mask, mask_score, mask_flag, mask_metrics = MaskQualityChecker.check_mask_quality(mask, bbox, img_size=(width, height))

            # Pre-Classification Crop Quality Gate
            is_valid_crop, crop_reason, crop_metrics = CropQualityChecker.check_crop_quality(crop, mask, category_group)

            if not is_valid_crop:
                logger.warning(f"Region {region_id} rejected by Crop Quality Gate: {crop_reason}")
                discarded_log.append({
                    "region_id": region_id,
                    "reason": f"CROP_QUALITY_REJECTED_{crop_reason}",
                    "details": crop_metrics
                })
                continue

            # Perceptual Hashing & Visual Embeddings
            hashes = self.visual_embedding_prov.compute_hashes(crop)
            crop_hash = hashes["sha256"]

            if crop_hash in crop_hashes_seen:
                logger.warning(f"DUPLICATE_CROP_HASH for {region_id}. Skipping duplicate card.")
                discarded_log.append({
                    "region_id": region_id,
                    "reason": "DUPLICATE_CROP_HASH",
                    "details": f"Crop hash {crop_hash[:8]} already processed"
                })
                continue
            crop_hashes_seen.add(crop_hash)

            # Save Crop & Mask to Static Storage
            image_url = self.storage_mgr.save_region_crop(analysis_id, region_id, crop)
            mask_url = self.storage_mgr.save_region_mask(analysis_id, region_id, mask)

            CropValidator.validate_region_crop(image_url, region_id)
            debug_crops.append((region_id, crop, crop_hash, image_url))

            # Mask-Only LAB Color Analysis
            color_result = self.color_analyzer.analyze_mask_crop(image_np, mask, bbox)

            # Fine-Grained Garment Attribute Classification
            garment_attr_res = self.model_mgr.garment_attributes.predict_attributes(crop)

            # FashionCLIP Candidate Ranking for Region
            fashionclip_rankings = self.model_mgr.fashionclip.rank_candidates(crop, category_group)

            # Footwear Classifier (if category_group == footwear)
            footwear_res = None
            if category_group == "footwear":
                footwear_res = self.model_mgr.footwear_classifier.classify_footwear_crop(crop, fashionclip_rankings)

            # Ensemble Evidence Classification
            classification = self.ensemble_classifier.classify_region(
                region_id=region_id,
                category_hint=category_group,
                detector_candidate_labels=region["candidate_labels"],
                fashionclip_rankings=fashionclip_rankings,
                vlm_analysis=vlm_analysis,
                models_detected=region["models_detected"]
            )

            # Dedicated footwear override if available
            if footwear_res and category_group == "footwear":
                fw_type = footwear_res["footwear_type"]
                classification["item_type"] = fw_type
                classification["category"] = "footwear"
                classification["display_name"] = ItemTaxonomyService.derive_display_name(fw_type)
                classification["confidence"] = footwear_res["confidence"]

            # Dynamic Formality & Fit Estimation
            item_formality = FormalityService.calculate_item_formality(classification["item_type"])
            fit_val, fit_conf, fit_needs_confirm = FitDetector.estimate_fit(mask, bbox, classification["item_type"])

            item_dict = {
                "region_id": region_id,
                "person_id": person_id,
                "category_group": category_group,
                "garment_type": classification["item_type"],
                "physical_layer": ItemTaxonomyService.derive_physical_layer(classification["item_type"]),
                "bbox": bbox,
                "crop_hash": crop_hash,
                "image_url": image_url,
                "mask_url": mask_url,
                "item_type": classification["item_type"],
                "category": classification["category"],
                "display_name": classification["display_name"],
                "color": color_result,
                "style": {"value": classification["category"], "confidence": classification["confidence"]},
                "fit": {"value": fit_val, "confidence": fit_conf},
                "material": {"value": "cotton", "confidence": 0.85},
                "garment_attributes": garment_attr_res,
                "formality": {"value": item_formality.value, "confidence": item_formality.confidence, "reasoning": item_formality.reasoning},
                "model_evidence": classification["model_evidence"],
                "provenance": {
                    "source_models": region["models_detected"],
                    "classification_source": "fashion_clip" if self.model_mgr.fashionclip.available else "ensemble_voting",
                    "mask_source": "sam2.1" if self.model_mgr.sam2.available else "grabcut",
                    "mask_metrics": mask_metrics,
                    "crop_metrics": crop_metrics
                },
                "needs_confirmation": classification["needs_confirmation"] or fit_needs_confirm or (not is_valid_mask),
                "confidence": classification["confidence"]
            }

            # Consistency Engine Validation
            item_dict = ConsistencyEngine.validate_and_correct_item(item_dict)
            evaluated_items.append(item_dict)

        # Stage 9: Outfit & Suit Relationship Reasoning
        is_suit, suit_confidence, matched_suit_ids = SuitDetector.detect_suit(evaluated_items, vlm_analysis.get("overall_outfit", {}))
        outfit_context_raw = FormalityService.calculate_outfit_formality(evaluated_items, is_suit)
        outfit_context_raw = ConsistencyEngine.validate_outfit_consistency(outfit_context_raw, evaluated_items, is_suit)

        # Pre-API Response Hard Validation Gates
        PipelineValidator.validate_pipeline_output(evaluated_items)

        overall_outfit = OverallOutfitContext(
            outfit_type="full suit" if is_suit else "outfit combo",
            style=outfit_context_raw["style"],
            formality=outfit_context_raw["formality"],
            occasion=["casual"] if outfit_context_raw["formality"] < 5 else ["formal", "business"],
            confidence=0.90
        )

        # Build Pydantic EvaluatedItemRegion objects
        pydantic_items: List[EvaluatedItemRegion] = []
        for it in evaluated_items:
            dom_colors = [
                DominantColor(name=c["name"], rgb=c["rgb"], percentage=c["percentage"])
                for c in it["color"].get("dominant_colors", [])
            ]
            color_detail = ColorDetailResult(
                primary=it["color"]["primary"],
                secondary=it["color"]["secondary"],
                dominant_colors=dom_colors,
                confidence=it["color"].get("confidence", 0.85)
            )

            title = f"{it['color']['primary']} {it['display_name']}" if it['color']['primary'] != "unknown" else it['display_name']

            region_obj = EvaluatedItemRegion(
                region_id=it["region_id"],
                person_id=it.get("person_id", "person_001"),
                category_group=it.get("category_group", "upper_body"),
                garment_type=it.get("garment_type", "casual_shirt"),
                physical_layer=it.get("physical_layer", "inner"),
                bbox=it["bbox"],
                crop_hash=it["crop_hash"],
                image_url=it["image_url"],
                mask_url=it["mask_url"],
                item_type=AttributeValueWithConfidence(value=it["item_type"], confidence=it["confidence"]),
                category=it["category"],
                display_name=it["display_name"],
                color=color_detail,
                style=AttributeValueWithConfidence(value=overall_outfit.style, confidence=0.88),
                fit=AttributeValueWithConfidence(value=it["fit"]["value"], confidence=0.85),
                material=AttributeValueWithConfidence(value=it["material"]["value"], confidence=0.85),
                formality=FormalityScoreDetail(value=it["formality"]["value"], confidence=0.90, reasoning=it["formality"].get("reasoning")),
                model_evidence=it["model_evidence"],
                provenance=it.get("provenance", {}),
                needs_confirmation=it["needs_confirmation"],
                
                id=it["region_id"],
                title=title,
                category_legacy=it["display_name"],
                suggested_metadata={
                    "item_type": it["item_type"],
                    "category": it["display_name"],
                    "title": title,
                    "primary_color": it["color"]["primary"],
                    "color_hex": "#0A192F" if it["color"]["primary"] in ["navy", "black"] else "#FFFFFF",
                    "formality": it["formality"]["value"],
                    "style": overall_outfit.style,
                    "confidence": it["confidence"],
                    "needs_confirmation": it["needs_confirmation"]
                }
            )
            pydantic_items.append(region_obj)

        # Build Person Groups
        person_groups: List[PersonGroup] = []
        for p in people_instances:
            pid = p["person_id"]
            p_garments = [it for it in pydantic_items if it.person_id == pid]
            person_groups.append(PersonGroup(person_id=pid, bbox=p["bbox"], garments=p_garments))

        # Save Visual Debug Run Output
        if os.environ.get("AI_DEBUG", "true").lower() == "true":
            self._save_debug_run(analysis_id, image_rgb, all_detections, fused_regions, debug_crops, evaluated_items, overall_outfit, discarded_log, provider_status)

        primary_item = pydantic_items[0] if pydantic_items else None

        return FullClothingAnalysisResponse(
            success=True,
            overall_outfit=overall_outfit,
            is_multi_item=len(pydantic_items) > 1,
            is_suit=is_suit,
            people=person_groups,
            items=pydantic_items,
            provider_status=provider_status,
            
            item_type=primary_item.item_type if primary_item else AttributeValueWithConfidence(value="unknown", confidence=0.0),
            category=AttributeValueWithConfidence(value=primary_item.display_name if primary_item else "unknown", confidence=0.0),
            primary_color=AttributeValueWithConfidence(value=primary_item.color.primary if primary_item else "unknown", confidence=0.0),
            dominant_colors=primary_item.color.dominant_colors if primary_item else [],
            pattern=AttributeValueWithConfidence(value="solid", confidence=0.85),
            style=AttributeValueWithConfidence(value=overall_outfit.style, confidence=0.85),
            fit=primary_item.fit if primary_item else AttributeValueWithConfidence(value="regular", confidence=0.85),
            material=primary_item.material if primary_item else AttributeValueWithConfidence(value="cotton", confidence=0.85),
            formality=FormalityScoreDetail(value=overall_outfit.formality, confidence=0.90)
        )

    def _save_debug_run(
        self,
        analysis_id: str,
        image_rgb: Image.Image,
        all_detections: List[Dict[str, Any]],
        fused_regions: List[Dict[str, Any]],
        debug_crops: List[Any],
        evaluated_items: List[Dict[str, Any]],
        overall_outfit: OverallOutfitContext,
        discarded_log: List[Dict[str, Any]],
        provider_status: Dict[str, Any]
    ):
        """Saves debug outputs, provenance, and annotated debug images to debug_runs/<timestamp>/."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            debug_dir = os.path.join("debug_runs", timestamp)
            os.makedirs(debug_dir, exist_ok=True)

            image_rgb.save(os.path.join(debug_dir, "original.png"))

            with open(os.path.join(debug_dir, "detections.json"), "w") as f:
                json.dump(all_detections, f, indent=2)

            with open(os.path.join(debug_dir, "discarded_candidates.json"), "w") as f:
                json.dump(discarded_log, f, indent=2)

            with open(os.path.join(debug_dir, "provider_status.json"), "w") as f:
                json.dump(provider_status, f, indent=2)

            for item in debug_crops:
                reg_id = item[0]
                crp = item[1]
                crp.save(os.path.join(debug_dir, f"crop_{reg_id}.png"), "PNG")

            with open(os.path.join(debug_dir, "final.json"), "w") as f:
                json.dump({
                    "analysis_id": analysis_id,
                    "overall_outfit": overall_outfit.model_dump(),
                    "items": evaluated_items
                }, f, indent=2)

            debug_img = image_rgb.copy()
            draw = ImageDraw.Draw(debug_img)

            for item in evaluated_items:
                region_id = item["region_id"]
                bbox = item["bbox"]
                display_name = item["display_name"]
                conf = item["confidence"]

                draw.rectangle(bbox, outline=(0, 255, 0), width=3)
                label_text = f"{region_id}: {display_name} ({conf:.2f})"
                draw.rectangle([bbox[0], max(0, bbox[1] - 25), bbox[0] + 240, bbox[1]], fill=(0, 255, 0))
                draw.text((bbox[0] + 5, max(0, bbox[1] - 20)), label_text, fill=(0, 0, 0))

            debug_img.save(os.path.join(debug_dir, "detections.png"))
            logger.info(f"Saved debug run artifacts to {debug_dir}")
        except Exception as e:
            logger.error(f"Failed to save debug run artifacts: {e}")

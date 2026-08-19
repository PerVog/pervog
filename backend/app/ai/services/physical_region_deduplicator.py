"""
Physical Region Deduplicator — Multi-Signal Deduplication Engine.

Collapses multi-model candidate detections for the SAME physical garment into ONE region card.
Enforces that different physical layers (inner vs outer, upper vs lower) are NEVER merged.
"""

from typing import List, Dict, Any
from PIL import Image
import numpy as np
import hashlib
import logging

from app.ai.services.physical_region_fusion import PhysicalRegionFusionEngine

logger = logging.getLogger(__name__)

def calculate_crop_sha256(crop: Image.Image) -> str:
    """Calculates SHA256 hash of the RGB pixel matrix of a crop."""
    crop_np = np.ascontiguousarray(np.array(crop.convert("RGB")))
    return hashlib.sha256(crop_np.tobytes()).hexdigest()

class PhysicalRegionDeduplicator:
    @staticmethod
    def deduplicate_and_fuse(detections: List[Dict[str, Any]], img_width: int, img_height: int) -> List[Dict[str, Any]]:
        engine = PhysicalRegionFusionEngine()
        fused_regions = engine.fuse_detections(detections, (img_width, img_height))
        results = []
        for reg in fused_regions:
            if hasattr(reg, "model_dump"):
                d = reg.model_dump()
            elif hasattr(reg, "dict"):
                d = reg.dict()
            else:
                d = dict(reg)
            d["cluster_size"] = len(d.get("candidate_labels", []))
            results.append(d)
        return results

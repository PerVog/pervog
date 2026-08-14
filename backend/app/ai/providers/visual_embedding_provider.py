"""
Visual Embedding Provider — Perceptual Hashes & Visual Feature Embedding Extractor.

Implements:
- SHA256 hash
- pHash (Perceptual Hash)
- dHash (Difference Hash)
- Visual Embedding Cosine Similarity (SigLIP / DINOv2 / CLIP)

Used strictly for physical-region matching and deduplication.
"""

from typing import Tuple, Dict, Any
from PIL import Image
import numpy as np
import hashlib
import cv2
import torch
import logging

logger = logging.getLogger(__name__)

def compute_dhash(image: Image.Image, hash_size: int = 8) -> str:
    """Computes difference hash (dHash) for an image crop."""
    resized = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = np.array(resized)
    # Compare adjacent pixels horizontally
    diff = pixels[:, 1:] > pixels[:, :-1]
    # Convert boolean array to hex string
    decimal_val = 0
    hex_str = ""
    for idx, value in enumerate(diff.flatten()):
        if value:
            decimal_val += 2 ** (idx % 4)
        if idx % 4 == 3:
            hex_str += f"{decimal_val:x}"
            decimal_val = 0
    return hex_str

def compute_phash(image: Image.Image, hash_size: int = 8) -> str:
    """Computes perceptual hash (pHash) for an image crop."""
    resized = image.convert("L").resize((32, 32), Image.Resampling.LANCZOS)
    pixels = np.array(resized, dtype=np.float32)
    # Discrete Cosine Transform (DCT)
    dct = cv2.dct(pixels)
    dct_low = dct[:hash_size, :hash_size]
    med = np.median(dct_low)
    diff = dct_low > med
    hex_str = ""
    decimal_val = 0
    for idx, value in enumerate(diff.flatten()):
        if value:
            decimal_val += 2 ** (idx % 4)
        if idx % 4 == 3:
            hex_str += f"{decimal_val:x}"
            decimal_val = 0
    return hex_str

def hamming_distance(hash1: str, hash2: str) -> int:
    """Calculates Hamming distance between two hex hashes of equal length."""
    if len(hash1) != len(hash2):
        return 64
    val1 = int(hash1, 16)
    val2 = int(hash2, 16)
    return bin(val1 ^ val2).count("1")

class VisualEmbeddingProvider:
    def __init__(self):
        self.model_id = "google/siglip-base-patch16-224"
        self.processor = None
        self.model = None
        self.available = False
        self._load_model()

    def _load_model(self):
        try:
            from transformers import AutoProcessor, AutoModel
            self.processor = AutoProcessor.from_pretrained(self.model_id)
            self.model = AutoModel.from_pretrained(self.model_id)
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
            self.model.eval()
            self.available = True
            logger.info("Visual Embedding model (SigLIP) initialized successfully.")
        except Exception as e:
            logger.warning(f"Visual Embedding model not available natively: {e}. Utilizing feature-aware fallback embeddings.")
            self.available = False

    def get_image_embedding(self, crop: Image.Image) -> np.ndarray:
        """Returns normalized 1D visual embedding vector for a crop image."""
        if self.available and self.model is not None and self.processor is not None:
            try:
                inputs = self.processor(images=crop, return_tensors="pt")
                if torch.cuda.is_available():
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}
                with torch.no_grad():
                    features = self.model.get_image_features(**inputs)
                    vec = features[0].cpu().numpy()
                    norm = np.linalg.norm(vec)
                    return vec / float(norm) if norm > 0 else vec
            except Exception as e:
                logger.error(f"Visual embedding error: {e}")

        # Color & texture histogram embedding fallback
        crop_np = np.array(crop.convert("RGB"))
        hist_r = np.histogram(crop_np[:, :, 0], bins=16, range=(0, 256))[0]
        hist_g = np.histogram(crop_np[:, :, 1], bins=16, range=(0, 256))[0]
        hist_b = np.histogram(crop_np[:, :, 2], bins=16, range=(0, 256))[0]
        vec = np.concatenate([hist_r, hist_g, hist_b]).astype(np.float32)
        norm = np.linalg.norm(vec)
        return vec / float(norm) if norm > 0 else vec

    def compute_hashes(self, crop: Image.Image) -> Dict[str, str]:
        """Computes SHA256, pHash, and dHash for a crop image."""
        crop_np = np.ascontiguousarray(np.array(crop.convert("RGB")))
        sha256_hash = hashlib.sha256(crop_np.tobytes()).hexdigest()
        phash_val = compute_phash(crop)
        dhash_val = compute_dhash(crop)
        return {
            "sha256": sha256_hash,
            "phash": phash_val,
            "dhash": dhash_val
        }

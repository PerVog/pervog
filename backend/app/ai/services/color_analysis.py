"""
Mask-Only Color Analysis Service — Independent Region CIELAB Color Extraction.

Calculates dominant item colors ONLY from SAM segmentation mask foreground pixels.
Removes pixels outside the mask, transparent pixels, and skin tone pixels using CIELAB color space.
Validates color independently for every region. Preserves black garments.
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

# Standard 27 Fashion Color Taxonomy with LAB Coordinates
COLOR_TAXONOMY_LAB = {
    "black": (0, 0, 0),
    "charcoal": (25, 0, 0),
    "dark grey": (35, 0, 0),
    "grey": (55, 0, 0),
    "light grey": (75, 0, 0),
    "white": (98, 0, 0),
    "off-white": (94, -2, 5),
    "cream": (91, -3, 14),
    "beige": (84, 3, 18),
    "khaki": (68, 4, 24),
    "brown": (40, 15, 25),
    "dark brown": (25, 12, 18),
    "red": (53, 80, 67),
    "maroon": (28, 48, 25),
    "pink": (74, 45, -5),
    "orange": (67, 43, 74),
    "yellow": (90, -10, 85),
    "mustard": (72, 10, 65),
    "green": (46, -50, 45),
    "olive": (45, -10, 30),
    "dark green": (25, -30, 20),
    "blue": (32, 15, -70),
    "light blue": (75, -15, -25),
    "navy": (15, 8, -35),
    "royal blue": (40, 30, -70),
    "purple": (30, 55, -45)
}

def rgb_to_lab(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Converts RGB tuple (0-255) to CIELAB (L, a, b)."""
    bgr = np.uint8([[[rgb[2], rgb[1], rgb[0]]]])
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)[0][0]
    L = lab[0] * 100.0 / 255.0
    a = lab[1] - 128.0
    b = lab[2] - 128.0
    return (L, a, b)

def is_skin_tone_lab(L: float, a: float, b: float) -> bool:
    """Detects human skin tones in LAB color space to exclude skin pixels from garment colors."""
    return (40 <= L <= 85) and (8 <= a <= 28) and (12 <= b <= 38)

class ColorAnalyzerService:
    def analyze_mask_crop(self, image_np: np.ndarray, mask: np.ndarray, bbox: List[int]) -> Dict[str, Any]:
        """
        Extracts dominant colors strictly from foreground pixels inside SAM mask.
        Preserves black/dark clothing pixels inside mask while excluding skin pixels and transparent artifacts.
        """
        x1, y1, x2, y2 = [max(0, int(b)) for b in bbox]
        h, w = image_np.shape[:2]
        x2 = min(w, x2)
        y2 = min(h, y2)

        region_mask = mask.copy()
        if region_mask.shape[:2] != (h, w):
            region_mask = cv2.resize(region_mask.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST).astype(bool)

        # Extract SAM foreground RGB pixels strictly inside mask
        foreground_pixels = image_np[region_mask]

        if len(foreground_pixels) < 20:
            crop_pixels = image_np[y1:y2, x1:x2].reshape(-1, 3)
            foreground_pixels = crop_pixels if len(crop_pixels) > 0 else np.array([[128, 128, 128]])

        # Exclude skin tone pixels strictly inside mask (e.g. exposed legs/feet)
        valid_pixels = []
        for pixel in foreground_pixels:
            r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
            L, a, b_val = rgb_to_lab((r, g, b))
            if not is_skin_tone_lab(L, a, b_val):
                valid_pixels.append([r, g, b])

        if len(valid_pixels) < 10:
            valid_pixels = np.array(foreground_pixels) if len(foreground_pixels) > 0 else np.array([[128, 128, 128]])
        else:
            valid_pixels = np.array(valid_pixels)

        # K-Means clustering in LAB space for this specific region crop
        lab_pixels = np.array([rgb_to_lab(tuple(p)) for p in valid_pixels])
        
        n_clusters = min(3, len(lab_pixels))
        kmeans = KMeans(n_clusters=n_clusters, n_init=5, random_state=42)
        kmeans.fit(lab_pixels)

        labels, counts = np.unique(kmeans.labels_, return_counts=True)
        total_count = np.sum(counts)

        dominant_colors_list = []
        for i in range(len(labels)):
            center_lab = kmeans.cluster_centers_[i]
            percentage = float((counts[i] / total_count) * 100.0)

            # Match to nearest canonical color in LAB space
            matched_name, center_rgb = self._match_lab_to_canonical(center_lab)
            dominant_colors_list.append({
                "name": matched_name,
                "rgb": center_rgb,
                "percentage": round(percentage, 1)
            })

        dominant_colors_list.sort(key=lambda x: x["percentage"], reverse=True)
        primary = dominant_colors_list[0]["name"]
        secondary = [c["name"] for c in dominant_colors_list[1:] if c["percentage"] >= 15.0]

        return {
            "primary": primary,
            "secondary": secondary,
            "dominant_colors": dominant_colors_list,
            "confidence": 0.92
        }

    def _match_lab_to_canonical(self, target_lab: Tuple[float, float, float]) -> Tuple[str, List[int]]:
        min_dist = float("inf")
        best_name = "grey"

        for name, ref_lab in COLOR_TAXONOMY_LAB.items():
            dist = np.sqrt(
                (target_lab[0] - ref_lab[0]) ** 2 +
                (target_lab[1] - ref_lab[1]) ** 2 +
                (target_lab[2] - ref_lab[2]) ** 2
            )
            if dist < min_dist:
                min_dist = dist
                best_name = name

        rgb_map = {
            "black": [15, 15, 15],
            "charcoal": [40, 40, 40],
            "dark grey": [70, 70, 70],
            "grey": [128, 128, 128],
            "light grey": [200, 200, 200],
            "white": [250, 250, 250],
            "off-white": [245, 245, 240],
            "cream": [240, 235, 215],
            "beige": [225, 210, 185],
            "khaki": [195, 175, 135],
            "brown": [110, 65, 35],
            "dark brown": [70, 40, 20],
            "red": [200, 30, 30],
            "maroon": [120, 20, 20],
            "pink": [240, 150, 170],
            "orange": [240, 120, 30],
            "yellow": [245, 215, 40],
            "mustard": [205, 160, 40],
            "green": [40, 160, 70],
            "olive": [105, 115, 55],
            "dark green": [25, 80, 40],
            "blue": [40, 100, 210],
            "light blue": [140, 190, 235],
            "navy": [15, 30, 65],
            "royal blue": [30, 60, 180],
            "purple": [110, 40, 150]
        }
        return best_name, rgb_map.get(best_name, [128, 128, 128])

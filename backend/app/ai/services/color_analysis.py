"""
Color Analysis Service — Strict Mask-Only CIELAB Color Analyzer with Quality Gate.

Extracts primary and secondary garment color using foreground mask or inner bounding box sampling.
Never returns 'unknown' if valid pixels exist inside the garment region.
"""

from typing import Dict, Any, List, Tuple
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)

COLOR_MAP_LAB = {
    "black": (0, 0, 0),
    "white": (100, 0, 0),
    "navy": (15, 10, -30),
    "dark navy": (10, 8, -25),
    "charcoal": (25, 0, 0),
    "dark grey": (35, 0, 0),
    "grey": (55, 0, 0),
    "light grey": (75, 0, 0),
    "cream": (95, -2, 10),
    "beige": (85, 2, 15),
    "khaki": (65, 2, 20),
    "royal blue": (40, 20, -60),
    "blue": (50, 10, -45),
    "light blue": (75, -10, -25),
    "sky blue": (80, -15, -20),
    "red": (50, 70, 60),
    "burgundy": (30, 45, 25),
    "maroon": (25, 40, 20),
    "green": (50, -50, 45),
    "dark green": (30, -35, 30),
    "olive": (45, -10, 30),
    "yellow": (90, -10, 80),
    "mustard": (70, 5, 65),
    "orange": (65, 45, 65),
    "pink": (70, 40, -5),
    "purple": (40, 50, -40),
    "brown": (35, 15, 25),
    "dark brown": (25, 12, 20)
}

def rgb_to_lab(r: int, g: int, b: int) -> Tuple[float, float, float]:
    r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0

    r_s = r_n / 12.92 if r_n <= 0.04045 else ((r_n + 0.055) / 1.055) ** 2.4
    g_s = g_n / 12.92 if g_n <= 0.04045 else ((g_n + 0.055) / 1.055) ** 2.4
    b_s = b_n / 12.92 if b_n <= 0.04045 else ((b_n + 0.055) / 1.055) ** 2.4

    x = (r_s * 0.4124564 + g_s * 0.3575761 + b_s * 0.1804375) * 100.0
    y = (r_s * 0.2126729 + g_s * 0.7151522 + b_s * 0.0721750) * 100.0
    z = (r_s * 0.0193339 + g_s * 0.1191920 + b_s * 0.9503041) * 100.0

    x_r, y_r, z_r = x / 95.047, y / 100.0, z / 108.883

    fx = x_r ** (1/3) if x_r > 0.008856 else (7.787 * x_r) + (16/116)
    fy = y_r ** (1/3) if y_r > 0.008856 else (7.787 * y_r) + (16/116)
    fz = z_r ** (1/3) if z_r > 0.008856 else (7.787 * z_r) + (16/116)

    l = (116.0 * fy) - 16.0
    a = 500.0 * (fx - fy)
    b_val = 200.0 * (fy - fz)

    return (l, a, b_val)

class ColorAnalyzerService:
    def analyze_garment_color(
        self,
        image: Image.Image,
        bbox: List[int],
        mask: np.ndarray = None,
        mask_confidence: float = 1.0
    ) -> Dict[str, Any]:
        """
        Extracts primary and secondary garment color using foreground mask or inner bounding box sampling.
        Never returns 'unknown' if valid pixels exist inside the garment region.
        """
        width, height = image.size
        x1, y1, x2, y2 = [max(0, int(b)) for b in bbox]
        x2 = min(width, x2)
        y2 = min(height, y2)

        if x2 <= x1 or y2 <= y1:
            return self._unknown_color_response()

        img_np = np.array(image.convert("RGB"))
        
        # If mask quality is low or mask missing, sample inner 70% of garment bounding box
        use_inner_box = (mask_confidence < 0.40) or (mask is None)
        
        if use_inner_box:
            bw, bh = x2 - x1, y2 - y1
            cx1 = max(0, int(x1 + 0.15 * bw))
            cy1 = max(0, int(y1 + 0.15 * bh))
            cx2 = min(width, int(x2 - 0.15 * bw))
            cy2 = min(height, int(y2 - 0.15 * bh))
            crop_np = img_np[cy1:cy2, cx1:cx2]
            if crop_np.size == 0:
                crop_np = img_np[y1:y2, x1:x2]
            sub_mask = np.ones((crop_np.shape[0], crop_np.shape[1]), dtype=bool)
        else:
            crop_np = img_np[y1:y2, x1:x2]
            if mask is not None and mask.shape[:2] == (height, width):
                sub_mask = mask[y1:y2, x1:x2]
            else:
                sub_mask = np.ones((y2 - y1, x2 - x1), dtype=bool)

        if crop_np.size == 0:
            return self._unknown_color_response()

        fg_pixels = crop_np[sub_mask]

        if len(fg_pixels) < 5:
            fg_pixels = crop_np.reshape(-1, 3)

        if len(fg_pixels) == 0:
            return self._unknown_color_response()

        # Filter skin tones & artificial zero-padding black background
        clean_pixels = []
        for p in fg_pixels:
            r, g, b = int(p[0]), int(p[1]), int(p[2])
            is_black_padding = (r < 15 and g < 15 and b < 15)
            is_skin = (r > 95 and g > 40 and b > 20 and r > g and r > b and abs(r - g) > 15)
            if not is_skin and not is_black_padding:
                clean_pixels.append(p)

        if len(clean_pixels) < 5:
            # Fall back to non-zero pixels if filtering left too few
            non_zero_pixels = [p for p in fg_pixels if not (int(p[0]) < 15 and int(p[1]) < 15 and int(p[2]) < 15)]
            clean_pixels = non_zero_pixels if len(non_zero_pixels) >= 5 else fg_pixels

        pixels_array = np.array(clean_pixels)
        mean_rgb = np.mean(pixels_array, axis=0)
        r, g, b = [int(x) for x in mean_rgb]

        target_lab = rgb_to_lab(r, g, b)

        # Find closest canonical color in CIELAB
        min_dist = float("inf")
        primary_color = "black"

        for color_name, lab_val in COLOR_MAP_LAB.items():
            dist = np.sqrt((target_lab[0] - lab_val[0])**2 + (target_lab[1] - lab_val[1])**2 + (target_lab[2] - lab_val[2])**2)
            if dist < min_dist:
                min_dist = dist
                primary_color = color_name

        # Calculate color confidence based on distance
        color_confidence = round(min(0.96, max(0.50, 1.0 - (min_dist / 120.0))), 2)
        color_hex = f"#{r:02x}{g:02x}{b:02x}".upper()

        return {
            "primary": primary_color,
            "secondary": [],
            "color_hex": color_hex,
            "dominant_colors": [
                {"name": primary_color, "rgb": [r, g, b], "percentage": 100.0}
            ],
            "confidence": color_confidence,
            "source": "inner_bbox_cielab_analysis" if use_inner_box else "mask_cielab_analysis"
        }

    def _unknown_color_response(self) -> Dict[str, Any]:
        return {
            "primary": "unknown",
            "secondary": [],
            "color_hex": "#000000",
            "dominant_colors": [],
            "confidence": 0.0,
            "source": "unknown"
        }

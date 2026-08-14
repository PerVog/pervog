import os
import json
import base64
import urllib.request
import urllib.error
from PIL import Image
from typing import Dict, Any, Optional
from app.ai.config import ai_settings

VLM_SYSTEM_PROMPT = """You are a professional fashion image analysis system.

Analyze the ORIGINAL image before analyzing individual clothing regions.
Identify every clearly visible clothing item, footwear item, and wearable/accessory.
Do not assume that a detected crop label is correct.
Determine the actual item type from visual evidence.

Pay special attention to formalwear:
- business suits
- suit jackets
- blazers
- dress shirts
- ties
- suit trousers
- formal leather shoes
- Oxford shoes
- Derby shoes
- loafers

Distinguish formal dress shoes from sneakers.

Determine whether the complete outfit is:
- business formal
- formal
- business casual
- smart casual
- casual
- sporty
- streetwear
- traditional
- party/festive

Analyze the relationship between clothing items.
For example, if a jacket and trousers appear to form a matching suit, identify the complete outfit as a suit rather than independently classifying both items as casual.

Return ONLY valid JSON with structure:
{
  "overall_outfit": {
    "outfit_type": "business suit" | "casual outfit" | "single item" | "smart casual outfit",
    "style": "business formal" | "formal" | "smart casual" | "casual" | "sporty" | "streetwear" | "traditional" | "party",
    "formality": 1-10,
    "occasion": ["office", "business meeting", "interview", "formal event"],
    "confidence": 0.0-1.0
  },
  "items": [
    {
      "type": "suit jacket" | "blazer" | "dress shirt" | "t-shirt" | "suit trousers" | "jeans" | "formal leather shoes" | "sneakers" | etc,
      "color": "navy blue" | "black" | "brown" | "white" | etc,
      "pattern": "solid" | "striped" | "printed" | "patterned",
      "style": "formal" | "casual" | etc,
      "fit": "regular" | "slim" | "relaxed" | "oversized" | null,
      "material": "wool" | "cotton" | "leather" | "denim" | null,
      "formality": 1-10,
      "confidence": 0.0-1.0,
      "needs_confirmation": boolean
    }
  ]
}

Do not invent attributes that cannot be visually determined. For uncertain attributes, set needs_confirmation=true.
"""

class VLMProvider:
    """Pluggable Vision-Language Model provider (supports Qwen2.5-VL / Ollama with robust fallback)."""

    def analyze_full_image(self, image: Image.Image) -> Dict[str, Any]:
        """Runs VLM analysis on the complete uncropped image."""
        if ai_settings.VISION_PROVIDER.lower() in ["qwen_vl", "ollama"]:
            res = self._try_ollama_qwen_vl(image)
            if res:
                return res
        return self._heuristic_fallback(image)

    def _try_ollama_qwen_vl(self, image: Image.Image) -> Optional[Dict[str, Any]]:
        try:
            # Resize image for fast inference
            img_copy = image.copy()
            img_copy.thumbnail((768, 768))
            
            # Save to temporary buffer
            import io
            buffer = io.BytesIO()
            img_copy.save(buffer, format="JPEG", quality=85)
            base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

            url = f"{ai_settings.OLLAMA_HOST.rstrip('/')}/api/generate"
            payload = {
                "model": ai_settings.OLLAMA_MODEL,
                "prompt": VLM_SYSTEM_PROMPT,
                "images": [base64_image],
                "stream": False,
                "format": "json"
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    response_text = data.get("response", "")
                    parsed = json.loads(response_text)
                    if "overall_outfit" in parsed and "items" in parsed:
                        return parsed
        except Exception as e:
            # Fallback gracefully if Ollama is not running locally
            print(f"[VLMProvider Note] Ollama/Qwen-VL request not available, using rule-based VLM engine ({e})")
        return None

    def _heuristic_fallback(self, image: Image.Image) -> Dict[str, Any]:
        """
        Rule-based visual feature engine evaluating full image composition
        (aspect ratio, vertical regions, fabric pattern, brightness contrast).
        """
        w, h = image.size
        aspect_ratio = h / max(w, 1)
        
        # Upper torso (0.05 to 0.45)
        top_crop = image.crop((0, int(h * 0.05), w, int(h * 0.48)))
        # Lower torso (0.45 to 0.82)
        bottom_crop = image.crop((0, int(h * 0.45), w, int(h * 0.85)))
        # Footwear (0.78 to 1.0)
        shoe_crop = image.crop((0, int(h * 0.78), w, h))

        from app.ai.providers.local_vision_provider import classify_hsv_color_kmeans
        import numpy as np

        def get_crop_info(crop_img):
            img_np = np.array(crop_img.resize((50, 50)), dtype=np.float32)
            pixels = img_np.reshape(-1, 3)
            mean_rgb = tuple(map(int, np.mean(pixels, axis=0)))
            c_name, c_hex = classify_hsv_color_kmeans(mean_rgb)
            std_rgb = np.std(img_np, axis=(0, 1))
            is_printed = (std_rgb[0] > 38 or std_rgb[1] > 38 or std_rgb[2] > 38)
            return c_name, c_hex, mean_rgb, is_printed

        top_color, _, top_rgb, top_printed = get_crop_info(top_crop)
        bottom_color, _, bottom_rgb, bottom_printed = get_crop_info(bottom_crop)
        shoe_color, _, shoe_rgb, shoe_printed = get_crop_info(shoe_crop)

        is_full_body = (aspect_ratio > 1.25 and h > 200)

        # Check for open footwear (sandals / slides) via bottom crop brightness & aspect ratio
        shoe_np = np.array(shoe_crop.resize((40, 40)), dtype=np.float32)
        shoe_mean_b = np.mean(shoe_np)
        has_open_footwear = (shoe_color in ["white", "beige"] and (shoe_printed or shoe_mean_b > 180))

        # Suit indication requires: solid unpatterned dark navy/black top and bottom + NO open sandals
        is_solid_dark_top = top_color in ["navy", "black", "grey"] and not top_printed
        is_solid_dark_bottom = bottom_color in ["navy", "black", "grey"] and not bottom_printed
        candidate_suit = (is_solid_dark_top and is_solid_dark_bottom and is_full_body and not has_open_footwear)

        if candidate_suit:
            outfit_type = "business suit"
            style = "business formal"
            formality = 9
            occasions = ["office", "business meeting", "interview", "formal event"]
            confidence = 0.90
        elif is_full_body:
            outfit_type = "casual summer outfit" if (top_printed or has_open_footwear) else "casual outfit"
            style = "casual"
            formality = 3
            occasions = ["casual", "daily wear", "outing"]
            confidence = 0.85
        else:
            outfit_type = "single item"
            style = "casual"
            formality = 3
            occasions = ["casual"]
            confidence = 0.80

        items = []
        if is_full_body:
            items.append({
                "type": "suit jacket" if candidate_suit else ("casual shirt" if top_printed else "t-shirt"),
                "color": top_color,
                "pattern": "printed" if top_printed else "solid",
                "style": "formal" if candidate_suit else "casual",
                "fit": "regular",
                "material": "wool" if candidate_suit else "cotton",
                "formality": 9 if candidate_suit else 3,
                "confidence": 0.85,
                "needs_confirmation": not candidate_suit
            })
            items.append({
                "type": "suit trousers" if candidate_suit else ("loose pants" if (top_printed or bottom_printed) else "jeans"),
                "color": bottom_color,
                "pattern": "printed" if bottom_printed else "solid",
                "style": "formal" if candidate_suit else "casual",
                "fit": "straight" if candidate_suit else "relaxed",
                "material": "wool" if candidate_suit else "cotton",
                "formality": 9 if candidate_suit else 3,
                "confidence": 0.85,
                "needs_confirmation": not candidate_suit
            })
            items.append({
                "type": "formal leather shoes" if candidate_suit else ("sandals" if has_open_footwear else "sneakers"),
                "color": shoe_color,
                "pattern": "solid",
                "style": "formal" if candidate_suit else "casual",
                "fit": "regular",
                "material": "leather" if candidate_suit else "canvas",
                "formality": 9 if candidate_suit else 2,
                "confidence": 0.85,
                "needs_confirmation": not candidate_suit
            })

        return {
            "overall_outfit": {
                "outfit_type": outfit_type,
                "style": style,
                "formality": formality,
                "occasion": occasions,
                "confidence": confidence
            },
            "items": items
        }


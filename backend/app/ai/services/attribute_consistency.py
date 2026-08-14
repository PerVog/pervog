from typing import List, Dict, Any, Tuple, Optional
from app.ai.taxonomy.categories import ITEM_TAXONOMY, CATEGORY_GROUPS

class AttributeConsistencyValidator:
    """
    Validates and enforces 100% attribute consistency across detected items and overall response payloads.
    Guarantees item_type is the single source of truth for category, title, style, and formality ranges.
    """

    @classmethod
    def normalize_item_type(cls, raw_type: str, category_name: str = "") -> str:
        """Maps arbitrary category string or raw item type to canonical item_type key."""
        t = (raw_type or category_name or "").lower().replace("-", "_").replace(" ", "_")

        if any(k in t for k in ["suit_jacket", "blazer_jacket", "tuxedo_jacket"]):
            return "suit_jacket"
        if "blazer" in t:
            return "blazer"
        if "dress_shirt" in t:
            return "dress_shirt"
        if any(k in t for k in ["casual_shirt", "resort_shirt", "printed_shirt", "hawaiian"]):
            return "casual_shirt"
        if "t_shirt" in t or "tshirt" in t:
            return "t_shirt"
        if "hoodie" in t or "sweatshirt" in t:
            return "hoodie"

        if "suit_trouser" in t or "suit_pant" in t:
            return "suit_trousers"
        if "formal_trouser" in t or "dress_pant" in t:
            return "formal_trousers"
        if any(k in t for k in ["loose_pant", "linen_pant", "casual_trouser", "wide_leg"]):
            return "loose_pants"
        if "jean" in t:
            return "jeans"
        if "chino" in t:
            return "chinos"
        if "jogger" in t or "track_pant" in t:
            return "joggers"
        if "short" in t:
            return "shorts"

        if any(k in t for k in ["formal_shoe", "formal_leather", "oxford_shoe", "derby_shoe", "dress_shoe"]):
            return "formal_leather_shoes"
        if "oxford" in t:
            return "oxford_shoes"
        if "loafer" in t:
            return "loafers"
        if "sandal" in t:
            return "sandals"
        if "slide" in t or "slipper" in t:
            return "slides"
        if any(k in t for k in ["sneaker", "running_shoe", "sports_shoe", "trainer"]):
            return "sneakers"

        # Default fallbacks
        if any(k in t for k in ["shoe", "boot"]):
            return "sneakers"
        if any(k in t for k in ["pant", "trouser"]):
            return "loose_pants"
        return "casual_shirt"

    @classmethod
    def validate_item(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates individual item attributes against its canonical item_type taxonomy.
        Ensures category, title, style, and formality match 100% without cross-contamination.
        """
        raw_type = item.get("item_type", item.get("type", item.get("category", "")))
        cat_name = item.get("category", "")
        
        canonical_key = cls.normalize_item_type(raw_type, cat_name)
        tax = ITEM_TAXONOMY.get(canonical_key, ITEM_TAXONOMY["casual_shirt"])

        # Check top-level primary_color first, then nested suggested_metadata
        color = item.get("primary_color") or item.get("color")
        if not color and "suggested_metadata" in item and isinstance(item["suggested_metadata"], dict):
            color = item["suggested_metadata"].get("primary_color") or item["suggested_metadata"].get("color")
        if not color:
            color = "blue"
        color = color.lower()
        
        item["primary_color"] = color

        # Enforce derived canonical fields
        item["item_type"] = canonical_key
        display_category = tax["display_name"]
        
        # FIX CATEGORY & TITLE CROSS-CONTAMINATION BUG (Requirement #1)
        item["category"] = display_category
        item["title"] = f"{color} {display_category}"
        
        # Synchronize suggested_metadata if present
        if "suggested_metadata" in item and isinstance(item["suggested_metadata"], dict):
            sm = item["suggested_metadata"]
            sm["item_type"] = canonical_key
            sm["type"] = display_category
            sm["suggested_category"] = display_category
            sm["primary_color"] = color
            sm["title"] = item["title"]


        # Enforce valid style and formality range
        current_style = item.get("style", tax["default_style"]).lower()
        if current_style not in ["formal", "business formal", "smart casual", "casual", "streetwear", "sporty", "traditional"]:
            current_style = tax["default_style"]
        item["style"] = current_style

        # Formality score validation
        f_range = tax["formality_range"]
        current_formality = item.get("formality", f_range[0])
        if current_formality < f_range[0] or current_formality > f_range[1]:
            # Clamp formality to valid range for item type
            clamped_formality = max(f_range[0], min(f_range[1], current_formality))
            print(f"[AI ATTRIBUTE VALIDATION DEBUG] Adjusted formality for {display_category}: original={current_formality} -> clamped={clamped_formality}")
            item["formality"] = clamped_formality

        return item

    @classmethod
    def validate_analysis(cls, response_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Top-level response validator. Ensures full payload consistency before returning API response.
        """
        items = response_payload.get("items", [])
        validated_items = [cls.validate_item(it) for it in items]
        response_payload["items"] = validated_items

        overall = response_payload.get("overall_outfit", {})
        is_suit = response_payload.get("is_suit", False)

        # Audit overall outfit context against validated items
        item_types = [it["item_type"] for it in validated_items]
        
        has_casual_items = any(t in ["sandals", "slides", "t_shirt", "casual_shirt", "loose_pants", "shorts", "sneakers"] for t in item_types)
        
        if is_suit and has_casual_items:
            print("[AI ATTRIBUTE VALIDATION DEBUG] Discrepancy found: is_suit=True but casual items detected. Revoking suit status.")
            response_payload["is_suit"] = False
            response_payload["suit_confidence"] = 0.0
            overall["outfit_type"] = "casual outfit"
            overall["style"] = "casual"
            overall["formality"] = 3
        
        response_payload["overall_outfit"] = overall
        return response_payload

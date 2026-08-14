"""
Item Taxonomy Service — Single Source of Truth for Fashion Item Types and Categories.

This module programmatically enforces that each item has exactly one canonical item_type,
which deterministically maps to its category (upper_body, lower_body, footwear, accessory),
display name, and default attributes.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ItemTaxonomyEntry(BaseModel):
    item_type: str
    category: str  # upper_body, lower_body, footwear, accessory
    display_name: str
    valid_styles: List[str]
    base_formality: int  # 1 to 10 scale baseline

CANONICAL_TAXONOMY: Dict[str, ItemTaxonomyEntry] = {
    # UPPER BODY
    "suit_jacket": ItemTaxonomyEntry(
        item_type="suit_jacket",
        category="upper_body",
        display_name="Suit Jacket",
        valid_styles=["business formal", "formal"],
        base_formality=9
    ),
    "blazer": ItemTaxonomyEntry(
        item_type="blazer",
        category="upper_body",
        display_name="Blazer",
        valid_styles=["smart casual", "formal", "business formal"],
        base_formality=7
    ),
    "dress_shirt": ItemTaxonomyEntry(
        item_type="dress_shirt",
        category="upper_body",
        display_name="Dress Shirt",
        valid_styles=["business formal", "formal", "smart casual"],
        base_formality=8
    ),
    "casual_shirt": ItemTaxonomyEntry(
        item_type="casual_shirt",
        category="upper_body",
        display_name="Casual Shirt",
        valid_styles=["casual", "smart casual"],
        base_formality=4
    ),
    "t_shirt": ItemTaxonomyEntry(
        item_type="t_shirt",
        category="upper_body",
        display_name="T-Shirt",
        valid_styles=["casual", "streetwear", "athletic"],
        base_formality=2
    ),
    "polo_shirt": ItemTaxonomyEntry(
        item_type="polo_shirt",
        category="upper_body",
        display_name="Polo Shirt",
        valid_styles=["casual", "smart casual"],
        base_formality=4
    ),
    "hoodie": ItemTaxonomyEntry(
        item_type="hoodie",
        category="upper_body",
        display_name="Hoodie",
        valid_styles=["casual", "streetwear", "athletic"],
        base_formality=2
    ),
    "sweater": ItemTaxonomyEntry(
        item_type="sweater",
        category="upper_body",
        display_name="Sweater",
        valid_styles=["casual", "smart casual"],
        base_formality=5
    ),
    "casual_jacket": ItemTaxonomyEntry(
        item_type="casual_jacket",
        category="upper_body",
        display_name="Casual Jacket",
        valid_styles=["casual", "streetwear", "smart casual"],
        base_formality=4
    ),
    "coat": ItemTaxonomyEntry(
        item_type="coat",
        category="upper_body",
        display_name="Coat",
        valid_styles=["formal", "smart casual", "business formal"],
        base_formality=7
    ),
    "kurta": ItemTaxonomyEntry(
        item_type="kurta",
        category="upper_body",
        display_name="Kurta",
        valid_styles=["traditional", "festive"],
        base_formality=6
    ),

    # LOWER BODY
    "suit_trousers": ItemTaxonomyEntry(
        item_type="suit_trousers",
        category="lower_body",
        display_name="Suit Trousers",
        valid_styles=["business formal", "formal"],
        base_formality=9
    ),
    "formal_trousers": ItemTaxonomyEntry(
        item_type="formal_trousers",
        category="lower_body",
        display_name="Formal Trousers",
        valid_styles=["formal", "business formal", "smart casual"],
        base_formality=8
    ),
    "loose_pants": ItemTaxonomyEntry(
        item_type="loose_pants",
        category="lower_body",
        display_name="Loose Pants",
        valid_styles=["casual", "streetwear"],
        base_formality=3
    ),
    "wide_leg_pants": ItemTaxonomyEntry(
        item_type="wide_leg_pants",
        category="lower_body",
        display_name="Wide Leg Pants",
        valid_styles=["casual", "streetwear", "smart casual"],
        base_formality=4
    ),
    "chinos": ItemTaxonomyEntry(
        item_type="chinos",
        category="lower_body",
        display_name="Chinos",
        valid_styles=["smart casual", "casual"],
        base_formality=5
    ),
    "jeans": ItemTaxonomyEntry(
        item_type="jeans",
        category="lower_body",
        display_name="Jeans",
        valid_styles=["casual", "streetwear", "smart casual"],
        base_formality=3
    ),
    "cargo_pants": ItemTaxonomyEntry(
        item_type="cargo_pants",
        category="lower_body",
        display_name="Cargo Pants",
        valid_styles=["casual", "streetwear"],
        base_formality=2
    ),
    "joggers": ItemTaxonomyEntry(
        item_type="joggers",
        category="lower_body",
        display_name="Joggers",
        valid_styles=["casual", "streetwear", "athletic"],
        base_formality=2
    ),
    "shorts": ItemTaxonomyEntry(
        item_type="shorts",
        category="lower_body",
        display_name="Shorts",
        valid_styles=["casual", "athletic"],
        base_formality=2
    ),

    # FOOTWEAR
    "formal_shoes": ItemTaxonomyEntry(
        item_type="formal_shoes",
        category="footwear",
        display_name="Formal Shoes",
        valid_styles=["business formal", "formal"],
        base_formality=9
    ),
    "oxford_shoes": ItemTaxonomyEntry(
        item_type="oxford_shoes",
        category="footwear",
        display_name="Oxford Shoes",
        valid_styles=["business formal", "formal"],
        base_formality=9
    ),
    "derby_shoes": ItemTaxonomyEntry(
        item_type="derby_shoes",
        category="footwear",
        display_name="Derby Shoes",
        valid_styles=["business formal", "formal", "smart casual"],
        base_formality=8
    ),
    "loafers": ItemTaxonomyEntry(
        item_type="loafers",
        category="footwear",
        display_name="Loafers",
        valid_styles=["smart casual", "casual", "formal"],
        base_formality=6
    ),
    "sneakers": ItemTaxonomyEntry(
        item_type="sneakers",
        category="footwear",
        display_name="Sneakers",
        valid_styles=["casual", "streetwear", "athletic"],
        base_formality=3
    ),
    "running_shoes": ItemTaxonomyEntry(
        item_type="running_shoes",
        category="footwear",
        display_name="Running Shoes",
        valid_styles=["athletic", "casual"],
        base_formality=2
    ),
    "sandals": ItemTaxonomyEntry(
        item_type="sandals",
        category="footwear",
        display_name="Sandals",
        valid_styles=["casual"],
        base_formality=2
    ),
    "slides": ItemTaxonomyEntry(
        item_type="slides",
        category="footwear",
        display_name="Slides",
        valid_styles=["casual", "athletic"],
        base_formality=1
    ),
    "boots": ItemTaxonomyEntry(
        item_type="boots",
        category="footwear",
        display_name="Boots",
        valid_styles=["casual", "smart casual", "streetwear"],
        base_formality=5
    ),

    # ACCESSORIES
    "tie": ItemTaxonomyEntry(
        item_type="tie",
        category="accessory",
        display_name="Tie",
        valid_styles=["business formal", "formal"],
        base_formality=9
    ),
    "belt": ItemTaxonomyEntry(
        item_type="belt",
        category="accessory",
        display_name="Belt",
        valid_styles=["business formal", "formal", "smart casual", "casual"],
        base_formality=6
    ),
    "watch": ItemTaxonomyEntry(
        item_type="watch",
        category="accessory",
        display_name="Watch",
        valid_styles=["business formal", "formal", "smart casual", "casual"],
        base_formality=6
    ),
    "glasses": ItemTaxonomyEntry(
        item_type="glasses",
        category="accessory",
        display_name="Glasses",
        valid_styles=["business formal", "formal", "smart casual", "casual"],
        base_formality=5
    ),
    "hat": ItemTaxonomyEntry(
        item_type="hat",
        category="accessory",
        display_name="Hat",
        valid_styles=["casual", "streetwear"],
        base_formality=2
    ),
    "bag": ItemTaxonomyEntry(
        item_type="bag",
        category="accessory",
        display_name="Bag",
        valid_styles=["business formal", "smart casual", "casual"],
        base_formality=5
    )
}

ALIAS_TO_CANONICAL: Dict[str, str] = {
    "pants": "loose_pants",
    "trousers": "formal_trousers",
    "shoes": "formal_shoes",
    "shirt": "casual_shirt",
    "jacket": "casual_jacket",
    "formal leather shoes": "formal_shoes",
    "oxford": "oxford_shoes",
    "derby": "derby_shoes",
    "sports shoes": "running_shoes",
    "flip flops": "slides",
    "hawaiian shirt": "casual_shirt",
    "printed shirt": "casual_shirt",
    "track pants": "joggers",
    "baggy pants": "loose_pants",
}

class ItemTaxonomyService:
    @staticmethod
    def normalize_item_type(raw_type: Any) -> str:
        """Converts raw string, dict, or alias into canonical item_type string."""
        if isinstance(raw_type, dict):
            raw_type = raw_type.get("value", "")
        
        raw_str = str(raw_type or "").strip()
        cleaned = raw_str.lower().replace(" ", "_").replace("-", "_")
        if cleaned in CANONICAL_TAXONOMY:
            return cleaned
        
        raw_lower = raw_str.lower()
        if raw_lower in ALIAS_TO_CANONICAL:
            return ALIAS_TO_CANONICAL[raw_lower]
        
        if "suit" in cleaned and "jacket" in cleaned:
            return "suit_jacket"
        if "blazer" in cleaned:
            return "blazer"
        if "dress" in cleaned and "shirt" in cleaned:
            return "dress_shirt"
        if "t_shirt" in cleaned or "tshirt" in cleaned:
            return "t_shirt"
        if "shirt" in cleaned:
            return "casual_shirt"
        if "suit" in cleaned and ("pant" in cleaned or "trouser" in cleaned):
            return "suit_trousers"
        if "formal" in cleaned and ("pant" in cleaned or "trouser" in cleaned):
            return "formal_trousers"
        if "loose" in cleaned and "pant" in cleaned:
            return "loose_pants"
        if "jean" in cleaned:
            return "jeans"
        if "pant" in cleaned or "trouser" in cleaned:
            return "loose_pants"
        if "sandal" in cleaned:
            return "sandals"
        if "slide" in cleaned:
            return "slides"
        if "sneaker" in cleaned:
            return "sneakers"
        if "boot" in cleaned:
            return "boots"
        if "shoe" in cleaned:
            return "formal_shoes"
            
        return "casual_shirt"

    @staticmethod
    def get_entry(item_type: Any) -> ItemTaxonomyEntry:
        canonical = ItemTaxonomyService.normalize_item_type(item_type)
        return CANONICAL_TAXONOMY.get(canonical, CANONICAL_TAXONOMY["casual_shirt"])

    @staticmethod
    def derive_category(item_type: Any) -> str:
        """Item type is the SINGLE SOURCE OF TRUTH for category."""
        entry = ItemTaxonomyService.get_entry(item_type)
        return entry.category

    @staticmethod
    def derive_display_name(item_type: Any) -> str:
        entry = ItemTaxonomyService.get_entry(item_type)
        return entry.display_name

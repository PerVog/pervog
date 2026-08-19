"""
Item Taxonomy Service — Single Source of Truth for Fashion Item Types, Category Groups, and Physical Layers.

This module programmatically enforces that each item has exactly one canonical item_type,
which deterministically maps to its category_group, garment_type, physical_layer, display_name, and default attributes.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ItemTaxonomyEntry(BaseModel):
    item_type: str
    category_group: str    # upper_body, outerwear, lower_body, full_body, footwear, accessory, unknown
    garment_type: str      # tshirt, blazer, dress_shirt, etc.
    physical_layer: str    # inner, outer, lower, full, footwear, accessory, unknown
    display_name: str
    valid_styles: List[str]
    base_formality: int    # 1 to 10 scale baseline

    @property
    def category(self) -> str:
        """Legacy compatibility property."""
        if self.category_group in ["upper_body", "outerwear"]:
            return "upper_body"
        return self.category_group

CANONICAL_TAXONOMY: Dict[str, ItemTaxonomyEntry] = {
    # UNKNOWN FALLBACK (NO SILENT CASUAL_SHIRT MUTATION)
    "unknown": ItemTaxonomyEntry(
        item_type="unknown",
        category_group="unknown",
        garment_type="unknown",
        physical_layer="unknown",
        display_name="Unknown Item",
        valid_styles=["casual"],
        base_formality=3
    ),

    # UPPER BODY - INNER LAYER
    "t_shirt": ItemTaxonomyEntry(
        item_type="t_shirt",
        category_group="upper_body",
        garment_type="tshirt",
        physical_layer="inner",
        display_name="T-Shirt",
        valid_styles=["casual", "streetwear", "athletic"],
        base_formality=2
    ),
    "casual_shirt": ItemTaxonomyEntry(
        item_type="casual_shirt",
        category_group="upper_body",
        garment_type="casual_shirt",
        physical_layer="inner",
        display_name="Casual Shirt",
        valid_styles=["casual", "smart casual"],
        base_formality=4
    ),
    "dress_shirt": ItemTaxonomyEntry(
        item_type="dress_shirt",
        category_group="upper_body",
        garment_type="dress_shirt",
        physical_layer="inner",
        display_name="Dress Shirt",
        valid_styles=["business formal", "formal", "smart casual"],
        base_formality=8
    ),
    "polo_shirt": ItemTaxonomyEntry(
        item_type="polo_shirt",
        category_group="upper_body",
        garment_type="polo_shirt",
        physical_layer="inner",
        display_name="Polo Shirt",
        valid_styles=["casual", "smart casual"],
        base_formality=4
    ),

    # UPPER BODY / OUTERWEAR - OUTER LAYER
    "suit_jacket": ItemTaxonomyEntry(
        item_type="suit_jacket",
        category_group="outerwear",
        garment_type="suit_jacket",
        physical_layer="outer",
        display_name="Suit Jacket",
        valid_styles=["business formal", "formal"],
        base_formality=9
    ),
    "blazer": ItemTaxonomyEntry(
        item_type="blazer",
        category_group="outerwear",
        garment_type="blazer",
        physical_layer="outer",
        display_name="Blazer",
        valid_styles=["smart casual", "formal", "business formal"],
        base_formality=7
    ),
    "casual_jacket": ItemTaxonomyEntry(
        item_type="casual_jacket",
        category_group="outerwear",
        garment_type="casual_jacket",
        physical_layer="outer",
        display_name="Casual Jacket",
        valid_styles=["casual", "streetwear", "smart casual"],
        base_formality=4
    ),
    "coat": ItemTaxonomyEntry(
        item_type="coat",
        category_group="outerwear",
        garment_type="coat",
        physical_layer="outer",
        display_name="Coat",
        valid_styles=["formal", "smart casual", "business formal"],
        base_formality=7
    ),
    "hoodie": ItemTaxonomyEntry(
        item_type="hoodie",
        category_group="outerwear",
        garment_type="hoodie",
        physical_layer="outer",
        display_name="Hoodie",
        valid_styles=["casual", "streetwear", "athletic"],
        base_formality=2
    ),
    "sweater": ItemTaxonomyEntry(
        item_type="sweater",
        category_group="upper_body",
        garment_type="sweater",
        physical_layer="outer",
        display_name="Sweater",
        valid_styles=["casual", "smart casual"],
        base_formality=5
    ),

    # FULL BODY GARMENTS
    "dress": ItemTaxonomyEntry(
        item_type="dress",
        category_group="full_body",
        garment_type="dress",
        physical_layer="full",
        display_name="Dress",
        valid_styles=["formal", "casual", "smart casual", "festive"],
        base_formality=7
    ),
    "saree": ItemTaxonomyEntry(
        item_type="saree",
        category_group="full_body",
        garment_type="saree",
        physical_layer="full",
        display_name="Saree",
        valid_styles=["traditional", "festive", "formal"],
        base_formality=8
    ),
    "kurta": ItemTaxonomyEntry(
        item_type="kurta",
        category_group="full_body",
        garment_type="kurta",
        physical_layer="full",
        display_name="Kurta",
        valid_styles=["traditional", "festive", "casual"],
        base_formality=6
    ),
    "jumpsuit": ItemTaxonomyEntry(
        item_type="jumpsuit",
        category_group="full_body",
        garment_type="jumpsuit",
        physical_layer="full",
        display_name="Jumpsuit",
        valid_styles=["casual", "smart casual", "formal"],
        base_formality=6
    ),

    # LOWER BODY - LOWER LAYER
    "suit_trousers": ItemTaxonomyEntry(
        item_type="suit_trousers",
        category_group="lower_body",
        garment_type="suit_trousers",
        physical_layer="lower",
        display_name="Suit Trousers",
        valid_styles=["business formal", "formal"],
        base_formality=9
    ),
    "formal_trousers": ItemTaxonomyEntry(
        item_type="formal_trousers",
        category_group="lower_body",
        garment_type="formal_trousers",
        physical_layer="lower",
        display_name="Formal Trousers",
        valid_styles=["formal", "business formal", "smart casual"],
        base_formality=8
    ),
    "loose_pants": ItemTaxonomyEntry(
        item_type="loose_pants",
        category_group="lower_body",
        garment_type="loose_pants",
        physical_layer="lower",
        display_name="Loose Pants",
        valid_styles=["casual", "streetwear"],
        base_formality=3
    ),
    "wide_leg_pants": ItemTaxonomyEntry(
        item_type="wide_leg_pants",
        category_group="lower_body",
        garment_type="wide_leg_pants",
        physical_layer="lower",
        display_name="Wide Leg Pants",
        valid_styles=["casual", "streetwear", "smart casual"],
        base_formality=4
    ),
    "chinos": ItemTaxonomyEntry(
        item_type="chinos",
        category_group="lower_body",
        garment_type="chinos",
        physical_layer="lower",
        display_name="Chinos",
        valid_styles=["smart casual", "casual"],
        base_formality=5
    ),
    "jeans": ItemTaxonomyEntry(
        item_type="jeans",
        category_group="lower_body",
        garment_type="jeans",
        physical_layer="lower",
        display_name="Jeans",
        valid_styles=["casual", "streetwear", "smart casual"],
        base_formality=3
    ),
    "cargo_pants": ItemTaxonomyEntry(
        item_type="cargo_pants",
        category_group="lower_body",
        garment_type="cargo_pants",
        physical_layer="lower",
        display_name="Cargo Pants",
        valid_styles=["casual", "streetwear"],
        base_formality=2
    ),
    "joggers": ItemTaxonomyEntry(
        item_type="joggers",
        category_group="lower_body",
        garment_type="joggers",
        physical_layer="lower",
        display_name="Joggers",
        valid_styles=["casual", "streetwear", "athletic"],
        base_formality=2
    ),
    "shorts": ItemTaxonomyEntry(
        item_type="shorts",
        category_group="lower_body",
        garment_type="shorts",
        physical_layer="lower",
        display_name="Shorts",
        valid_styles=["casual", "athletic"],
        base_formality=2
    ),
    "skirt": ItemTaxonomyEntry(
        item_type="skirt",
        category_group="lower_body",
        garment_type="skirt",
        physical_layer="lower",
        display_name="Skirt",
        valid_styles=["casual", "smart casual", "formal"],
        base_formality=5
    ),

    # FOOTWEAR
    "formal_shoes": ItemTaxonomyEntry(
        item_type="formal_shoes",
        category_group="footwear",
        garment_type="formal_shoes",
        physical_layer="footwear",
        display_name="Formal Shoes",
        valid_styles=["business formal", "formal"],
        base_formality=9
    ),
    "oxford_shoes": ItemTaxonomyEntry(
        item_type="oxford_shoes",
        category_group="footwear",
        garment_type="oxford_shoes",
        physical_layer="footwear",
        display_name="Oxford Shoes",
        valid_styles=["business formal", "formal"],
        base_formality=9
    ),
    "derby_shoes": ItemTaxonomyEntry(
        item_type="derby_shoes",
        category_group="footwear",
        garment_type="derby_shoes",
        physical_layer="footwear",
        display_name="Derby Shoes",
        valid_styles=["business formal", "formal", "smart casual"],
        base_formality=8
    ),
    "loafers": ItemTaxonomyEntry(
        item_type="loafers",
        category_group="footwear",
        garment_type="loafers",
        physical_layer="footwear",
        display_name="Loafers",
        valid_styles=["smart casual", "casual", "formal"],
        base_formality=6
    ),
    "sneakers": ItemTaxonomyEntry(
        item_type="sneakers",
        category_group="footwear",
        garment_type="sneakers",
        physical_layer="footwear",
        display_name="Sneakers",
        valid_styles=["casual", "streetwear", "athletic"],
        base_formality=3
    ),
    "running_shoes": ItemTaxonomyEntry(
        item_type="running_shoes",
        category_group="footwear",
        garment_type="running_shoes",
        physical_layer="footwear",
        display_name="Running Shoes",
        valid_styles=["athletic", "casual"],
        base_formality=2
    ),
    "sandals": ItemTaxonomyEntry(
        item_type="sandals",
        category_group="footwear",
        garment_type="sandals",
        physical_layer="footwear",
        display_name="Sandals",
        valid_styles=["casual"],
        base_formality=2
    ),
    "slides": ItemTaxonomyEntry(
        item_type="slides",
        category_group="footwear",
        garment_type="slides",
        physical_layer="footwear",
        display_name="Slides",
        valid_styles=["casual", "athletic"],
        base_formality=1
    ),
    "boots": ItemTaxonomyEntry(
        item_type="boots",
        category_group="footwear",
        garment_type="boots",
        physical_layer="footwear",
        display_name="Boots",
        valid_styles=["casual", "smart casual", "streetwear"],
        base_formality=5
    ),

    # ACCESSORIES
    "tie": ItemTaxonomyEntry(
        item_type="tie",
        category_group="accessory",
        garment_type="tie",
        physical_layer="accessory",
        display_name="Tie",
        valid_styles=["business formal", "formal"],
        base_formality=9
    ),
    "belt": ItemTaxonomyEntry(
        item_type="belt",
        category_group="accessory",
        garment_type="belt",
        physical_layer="accessory",
        display_name="Belt",
        valid_styles=["business formal", "formal", "smart casual", "casual"],
        base_formality=6
    ),
    "watch": ItemTaxonomyEntry(
        item_type="watch",
        category_group="accessory",
        garment_type="watch",
        physical_layer="accessory",
        display_name="Watch",
        valid_styles=["business formal", "formal", "smart casual", "casual"],
        base_formality=6
    ),
    "glasses": ItemTaxonomyEntry(
        item_type="glasses",
        category_group="accessory",
        garment_type="glasses",
        physical_layer="accessory",
        display_name="Glasses",
        valid_styles=["business formal", "formal", "smart casual", "casual"],
        base_formality=5
    ),
    "hat": ItemTaxonomyEntry(
        item_type="hat",
        category_group="accessory",
        garment_type="hat",
        physical_layer="accessory",
        display_name="Hat",
        valid_styles=["casual", "streetwear"],
        base_formality=2
    ),
    "bag": ItemTaxonomyEntry(
        item_type="bag",
        category_group="accessory",
        garment_type="bag",
        physical_layer="accessory",
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
    "upper_body": "casual_shirt",
    "lower_body": "loose_pants",
    "footwear": "formal_shoes",
    "outerwear": "casual_jacket",
    "accessory": "belt",
    "short_sleeve_top": "t_shirt",
    "long_sleeve_top": "casual_shirt",
    "short_sleeve_outwear": "casual_jacket",
    "long_sleeve_outwear": "blazer",
    "vest": "sweater",
    "sling": "t_shirt",
    "short_sleeve_dress": "dress",
    "long_sleeve_dress": "dress",
    "vest_dress": "dress",
    "sling_dress": "dress",
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
        
        if "saree" in cleaned or "sari" in cleaned:
            return "saree"
        if "kurta" in cleaned:
            return "kurta"
        if "dress" in cleaned and "shirt" not in cleaned:
            return "dress"
        if "jumpsuit" in cleaned:
            return "jumpsuit"
        if "suit" in cleaned and "jacket" in cleaned:
            return "suit_jacket"
        if "blazer" in cleaned:
            return "blazer"
        if "dress" in cleaned and "shirt" in cleaned:
            return "dress_shirt"
        if "t_shirt" in cleaned or "tshirt" in cleaned:
            return "t_shirt"
        if "shirt" in cleaned and "unused" not in cleaned:
            return "casual_shirt"
        if "suit" in cleaned and ("pant" in cleaned or "trouser" in cleaned):
            return "suit_trousers"
        if "formal" in cleaned and ("pant" in cleaned or "trouser" in cleaned):
            return "formal_trousers"
        if "loose" in cleaned and "pant" in cleaned:
            return "loose_pants"
        if "jean" in cleaned:
            return "jeans"
        if "skirt" in cleaned:
            return "skirt"
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
        if "tie" in cleaned:
            return "tie"
        if "belt" in cleaned:
            return "belt"
        if "watch" in cleaned:
            return "watch"
        if "glass" in cleaned:
            return "glasses"
        if "hat" in cleaned or "cap" in cleaned:
            return "hat"
        if "bag" in cleaned:
            return "bag"
            
        return "unknown"

    @staticmethod
    def get_entry(item_type: Any) -> ItemTaxonomyEntry:
        canonical = ItemTaxonomyService.normalize_item_type(item_type)
        return CANONICAL_TAXONOMY.get(canonical, CANONICAL_TAXONOMY["unknown"])

    @staticmethod
    def derive_category_group(item_type: Any) -> str:
        entry = ItemTaxonomyService.get_entry(item_type)
        return entry.category_group

    @staticmethod
    def derive_physical_layer(item_type: Any) -> str:
        entry = ItemTaxonomyService.get_entry(item_type)
        return entry.physical_layer

    @staticmethod
    def derive_category(item_type: Any) -> str:
        """Item type is the SINGLE SOURCE OF TRUTH for category."""
        entry = ItemTaxonomyService.get_entry(item_type)
        return entry.category

    @staticmethod
    def derive_display_name(item_type: Any) -> str:
        entry = ItemTaxonomyService.get_entry(item_type)
        return entry.display_name

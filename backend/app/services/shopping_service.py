from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.wardrobe import WardrobeItem
from app.schemas.shopping import ShoppingGapResponse, ShoppingGapRecommendation
from app.recommendation.color_rules import ColorCompatibilityService

STAPLE_ITEMS = [
    {
        "category": "Shoes",
        "suggested_item": "Classic White Sneakers",
        "color": "white",
        "reason": "Versatile neutral footwear that pairs seamlessly with jeans, shorts, and casual trousers."
    },
    {
        "category": "Jacket",
        "suggested_item": "Classic Denim Jacket",
        "color": "blue",
        "reason": "Essential layering piece for spring and autumn outfits."
    },
    {
        "category": "Pants",
        "suggested_item": "Navy Slim Chinos",
        "color": "navy",
        "reason": "High-utility smart casual bottom that bridges casual and formal dress codes."
    },
    {
        "category": "Shirt",
        "suggested_item": "White Oxford Button-Down Shirt",
        "color": "white",
        "reason": "Timeless wardrobe foundation item compatible with almost all pants and jackets."
    },
    {
        "category": "Watch",
        "suggested_item": "Minimalist Leather Strap Watch",
        "color": "brown",
        "reason": "Subtle accessory that instantly elevates casual and smart casual outfits."
    },
    {
        "category": "T-Shirt",
        "suggested_item": "Black Crewneck Cotton Tee",
        "color": "black",
        "reason": "Anchor piece for monochrome and layered outfits."
    }
]

class ShoppingService:
    def __init__(self, db: Session):
        self.db = db

    def analyze_wardrobe_gaps(self, user_id: int) -> ShoppingGapResponse:
        items = self.db.query(WardrobeItem).filter(WardrobeItem.user_id == user_id).all()
        
        existing_categories = set(it.category for it in items)
        existing_colors = [it.attributes.primary_color for it in items if it.attributes]

        tops = [it for it in items if it.category in ["Shirt", "T-Shirt", "Polo", "Hoodie", "Sweater"]]
        bottoms = [it for it in items if it.category in ["Pants", "Jeans", "Shorts", "Trousers"]]

        gaps = []

        for staple in STAPLE_ITEMS:
            staple_cat = staple["category"]
            staple_color = staple["color"]

            # Calculate compatible tops and bottoms
            comp_tops = 0
            for t in tops:
                t_color = t.attributes.primary_color if t.attributes else "white"
                score = ColorCompatibilityService.get_color_score(staple_color, t_color)
                if score >= 80:
                    comp_tops += 1

            comp_bottoms = 0
            for b in bottoms:
                b_color = b.attributes.primary_color if b.attributes else "blue"
                score = ColorCompatibilityService.get_color_score(staple_color, b_color)
                if score >= 80:
                    comp_bottoms += 1

            potential_outfits = max(1, comp_tops * comp_bottoms) if (comp_tops > 0 and comp_bottoms > 0) else (comp_tops + comp_bottoms) * 2

            # Evaluate score level
            if potential_outfits > 15:
                usefulness = "EXCELLENT"
            elif potential_outfits > 8:
                usefulness = "HIGH"
            else:
                usefulness = "MEDIUM"

            gaps.append(ShoppingGapRecommendation(
                category=staple_cat,
                suggested_item=staple["suggested_item"],
                color=staple_color,
                reason=staple["reason"],
                compatible_tops_count=comp_tops,
                compatible_bottoms_count=comp_bottoms,
                potential_outfits_unlocked=potential_outfits,
                usefulness_score=usefulness
            ))

        # Sort gaps by potential outfits unlocked descending
        gaps.sort(key=lambda x: x.potential_outfits_unlocked, reverse=True)

        return ShoppingGapResponse(
            user_id=user_id,
            total_wardrobe_count=len(items),
            missing_gaps=gaps
        )

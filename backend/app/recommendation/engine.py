import random
from typing import List, Dict, Any, Optional
from app.models.wardrobe import WardrobeItem
from app.recommendation.ranker import RuleBasedRanker

# Category mappings to standard roles
TOP_CATEGORIES = {"Shirt", "T-Shirt", "Polo", "Hoodie", "Sweater", "Kurta"}
BOTTOM_CATEGORIES = {"Pants", "Jeans", "Shorts", "Trousers", "Skirt"}
FOOTWEAR_CATEGORIES = {"Shoes", "Sneakers", "Sandals", "Boots"}
OUTERWEAR_CATEGORIES = {"Jacket", "Coat"}
ACCESSORY_CATEGORIES = {"Watch", "Belt", "Cap", "Hat", "Bag", "Glasses"}

class RecommendationEngine:
    def __init__(self, ranker=None):
        self.ranker = ranker or RuleBasedRanker()

    def _categorize_item_role(self, item: WardrobeItem) -> str:
        cat = item.category
        if cat in TOP_CATEGORIES:
            return "top"
        if cat in BOTTOM_CATEGORIES:
            return "bottom"
        if cat in FOOTWEAR_CATEGORIES:
            return "footwear"
        if cat in OUTERWEAR_CATEGORIES:
            return "jacket"
        if cat in ACCESSORY_CATEGORIES:
            return "accessory"
        return "top" # Default

    def _extract_attribute_dict(self, item: WardrobeItem) -> Dict[str, Any]:
        attr = item.attributes
        if not attr:
            return {
                "category": item.category,
                "primary_color": "white",
                "formality": 3,
                "warmth": 1,
                "material": "cotton",
                "fit": "regular",
                "style": "casual",
                "condition": "good",
                "occasions": ["casual"]
            }
        return {
            "category": item.category,
            "primary_color": attr.primary_color,
            "formality": attr.formality or 3,
            "warmth": attr.warmth or 1,
            "material": attr.material or "cotton",
            "fit": attr.fit or "regular",
            "style": attr.style or "casual",
            "condition": attr.condition or "good",
            "occasions": attr.occasions or ["casual"]
        }

    def generate_recommendations(
        self,
        wardrobe_items: List[WardrobeItem],
        context: Dict[str, Any],
        selected_item_id: Optional[int] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        # Filter available items
        available_items = [it for it in wardrobe_items if it.is_available]
        if not available_items:
            return []

        # Partition items by role
        tops, bottoms, footwear, jackets, accessories = [], [], [], [], []
        
        selected_item = None
        for it in available_items:
            if selected_item_id and it.id == selected_item_id:
                selected_item = it

            role = self._categorize_item_role(it)
            item_entry = {
                "db_item": it,
                "role": role,
                "attribute_dict": self._extract_attribute_dict(it)
            }
            if role == "top":
                tops.append(item_entry)
            elif role == "bottom":
                bottoms.append(item_entry)
            elif role == "footwear":
                footwear.append(item_entry)
            elif role == "jacket":
                jackets.append(item_entry)
            elif role == "accessory":
                accessories.append(item_entry)

        # Fallback if missing core categories
        if not tops:
            tops = bottoms or footwear or [{"db_item": available_items[0], "role": "top", "attribute_dict": self._extract_attribute_dict(available_items[0])}]
        if not bottoms:
            bottoms = tops
        if not footwear:
            footwear = tops

        # Build candidate combinations
        candidates = []
        
        if selected_item:
            selected_role = self._categorize_item_role(selected_item)
            selected_entry = {
                "db_item": selected_item,
                "role": selected_role,
                "attribute_dict": self._extract_attribute_dict(selected_item)
            }
            
            # Match selected item with complementary roles
            candidate_tops = [selected_entry] if selected_role == "top" else tops
            candidate_bottoms = [selected_entry] if selected_role == "bottom" else bottoms
            candidate_footwear = [selected_entry] if selected_role == "footwear" else footwear
            candidate_jackets = [selected_entry] if selected_role == "jacket" else jackets

            for t in candidate_tops[:8]:
                for b in candidate_bottoms[:8]:
                    for f in candidate_footwear[:6]:
                        combo_items = [t, b, f]
                        if selected_role == "jacket":
                            combo_items.append(selected_entry)
                        elif jackets and random.random() > 0.5:
                            combo_items.append(jackets[0])
                        if accessories and random.random() > 0.5:
                            combo_items.append(accessories[0])

                        # Ensure selected item is included
                        if any(x["db_item"].id == selected_item.id for x in combo_items):
                            candidates.append({"items": combo_items})
        else:
            # Full outfit combinatorial generator
            for t in tops[:10]:
                for b in bottoms[:10]:
                    for f in footwear[:8]:
                        combo_items = [t, b, f]
                        # Optionally add jacket if temperature cool or random
                        temp_c = context.get("temperature_c", 22.0)
                        if jackets and (temp_c < 18 or random.random() > 0.6):
                            j_choice = random.choice(jackets)
                            combo_items.append(j_choice)

                        if accessories and random.random() > 0.5:
                            a_choice = random.choice(accessories)
                            combo_items.append(a_choice)

                        candidates.append({"items": combo_items})

        if not candidates:
            # Fallback single candidate
            candidates = [{"items": [tops[0], bottoms[0], footwear[0]]}]

        # Limit candidate evaluation to top 50 combinations for speed
        if len(candidates) > 60:
            random.shuffle(candidates)
            candidates = candidates[:60]

        # Rank candidates using RuleBasedRanker
        ranked_results = self.ranker.rank(candidates, context)

        # Format output
        formatted_outfits = []
        for res in ranked_results[:limit]:
            cand = res["candidate"]
            item_details = []
            title_parts = []
            
            for entry in cand["items"]:
                db_item = entry["db_item"]
                item_details.append({
                    "role": entry["role"],
                    "item": db_item
                })
                title_parts.append(db_item.title)

            title_str = " + ".join(title_parts[:3])
            
            formatted_outfits.append({
                "title": title_str,
                "occasion": context.get("occasion", "Casual"),
                "weather_condition": context.get("weather_condition", "Clear"),
                "temperature_c": context.get("temperature_c", 22.0),
                "score": res["score"],
                "score_breakdown": res["score_breakdown"],
                "reasons": res["reasons"],
                "items": item_details
            })

        return formatted_outfits

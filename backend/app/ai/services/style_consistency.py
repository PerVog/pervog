from typing import List, Dict, Any, Tuple

class StyleConsistencyValidator:
    """
    Validates consistency between individual clothing items, item styles, overall outfit style, and formality score.
    Detects and resolves contradictions (e.g. Business Formal outfit style with sandals, casual printed shirts, or loose beach pants).
    """

    CASUAL_INDICATORS = {
        "items": ["sandals", "slides", "flip flops", "t-shirt", "casual shirt", "loose pants", "wide leg pants", "shorts", "joggers", "sneakers"],
        "patterns": ["printed", "graphic", "floral", "hawaiian"],
        "materials": ["denim", "linen", "fleece", "canvas"]
    }

    FORMAL_INDICATORS = {
        "items": ["suit jacket", "blazer", "suit trousers", "formal trousers", "dress shirt", "formal shoes", "oxford shoes", "derby shoes", "tie", "bow tie"],
        "materials": ["wool", "silk"]
    }

    @classmethod
    def validate_and_correct(
        self,
        items: List[Dict[str, Any]],
        overall_context: Dict[str, Any],
        is_suit: bool = False
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], bool]:
        """
        Audits predictions and resolves any style contradictions.
        Returns (corrected_overall_context, corrected_items, style_conflict_found).
        """
        item_types = [it.get("type", "").lower() for it in items]
        item_styles = [it.get("style", "").lower() for it in items]
        
        overall_style = overall_context.get("style", "casual").lower()
        overall_formality = overall_context.get("formality", 3)

        # Count casual vs formal visual signals across all detected items
        casual_count = 0
        formal_count = 0

        has_sandals = False
        has_casual_shirt = False
        has_loose_pants = False

        for it in items:
            t = it.get("type", "").lower()
            pattern = it.get("pattern", "").lower()
            
            if any(c in t for c in ["sandal", "slide", "flip flop"]):
                has_sandals = True
                casual_count += 3
            elif "sneaker" in t:
                casual_count += 2
            elif any(c in t for c in ["t-shirt", "casual shirt", "hawaiian"]):
                has_casual_shirt = True
                casual_count += 2
            elif any(c in t for c in ["loose pants", "wide leg", "shorts", "joggers"]):
                has_loose_pants = True
                casual_count += 2

            if pattern in self.CASUAL_INDICATORS["patterns"]:
                casual_count += 1

            if any(f in t for f in ["suit jacket", "blazer"]):
                formal_count += 2
            elif any(f in t for f in ["suit trousers", "formal trousers"]):
                formal_count += 2
            elif any(f in t for f in ["formal shoes", "oxford", "derby", "dress shirt"]):
                formal_count += 2

        # Detect contradiction: Overall style predicted as Formal / Business Formal, but items are overwhelmingly casual
        is_formal_prediction = (overall_style in ["business formal", "formal"] or overall_formality >= 7 or is_suit)
        has_strong_casual_evidence = (has_sandals or (casual_count >= 3 and not is_suit))

        style_conflict = False
        if is_formal_prediction and has_strong_casual_evidence:
            style_conflict = True
            print(f"[AI ANALYSIS DEBUG] StyleConsistencyValidator DETECTED CONTRADICTION: Overall={overall_style} Formality={overall_formality}, but items have strong casual evidence (casual_count={casual_count}, sandals={has_sandals}). Correcting to Casual.")
            
            # Correct overall context
            overall_context["outfit_type"] = "casual summer outfit" if (has_sandals or has_casual_shirt) else "casual outfit"
            overall_context["style"] = "casual"
            overall_context["formality"] = 3
            overall_context["confidence"] = 0.90

            # Correct items if they were improperly forced to formal categories
            for it in items:
                t = it.get("type", "").lower()
                p_color = it.get("primary_color", it.get("color", "blue"))
                c_hex = it.get("color_hex", "#0D6EFD")
                
                it["primary_color"] = p_color
                it["color_hex"] = c_hex

                if "suit jacket" in t or "blazer" in t:
                    if has_casual_shirt or pattern in ["printed", "graphic"]:
                        it["type"] = "casual shirt"
                        it["category"] = "Casual Shirt"
                        it["style"] = "casual"
                        it["formality"] = 3
                elif "suit trousers" in t or "formal trousers" in t:
                    if has_loose_pants or pattern in ["printed", "graphic"]:
                        it["type"] = "loose pants"
                        it["category"] = "Loose Pants"
                        it["style"] = "casual"
                        it["formality"] = 3
                elif "formal shoes" in t or "oxford" in t:
                    if has_sandals:
                        it["type"] = "sandals"
                        it["category"] = "Sandals"
                        it["style"] = "casual"
                        it["formality"] = 2


        return overall_context, items, style_conflict

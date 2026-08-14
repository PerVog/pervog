from typing import List, Dict, Any, Tuple
from app.recommendation.color_rules import ColorCompatibilityService
from app.recommendation.occasion_rules import OccasionService

class ColorScorer:
    def score(self, items: List[Dict[str, Any]]) -> Tuple[float, str]:
        colors = [it.get("primary_color", "white") for it in items if it]
        score_val = ColorCompatibilityService.evaluate_outfit_colors(colors)
        if score_val >= 90:
            reason = "✓ Excellent color harmony"
        elif score_val >= 75:
            reason = "✓ Balanced color combination"
        else:
            reason = "⚠ Color combination may clash"
        return score_val, reason

class OccasionScorer:
    def score(self, items: List[Dict[str, Any]], occasion: str) -> Tuple[float, str]:
        if not items:
            return 80.0, "✓ Suitable for occasion"
        scores = []
        for it in items:
            formality = it.get("formality", 3)
            item_occ = it.get("occasions", [])
            scores.append(OccasionService.score_item_for_occasion(formality, item_occ, occasion))
        avg_score = sum(scores) / len(scores)
        reason = f"✓ Appropriate formality for {occasion}" if avg_score >= 75 else f"⚠ May be slightly out of formality for {occasion}"
        return avg_score, reason

class WeatherScorer:
    def score(self, items: List[Dict[str, Any]], temp_c: float, rain_prob: int) -> Tuple[float, str]:
        if not items:
            return 80.0, "✓ Weather appropriate"

        score_acc = 100.0
        reasons = []

        # Temperature check
        if temp_c is not None:
            if temp_c > 30:
                for it in items:
                    warmth = it.get("warmth", 1)
                    material = str(it.get("material", "")).lower()
                    if warmth > 3 or material in ["wool", "leather", "fleece"]:
                        score_acc -= 25.0
                reasons.append("Comfortable for hot temperature (>30°C)")
            elif temp_c < 15:
                has_outerwear_or_warmth = any(it.get("warmth", 1) >= 2 or it.get("category", "") in ["Jacket", "Coat", "Sweater", "Hoodie"] for it in items)
                if not has_outerwear_or_warmth:
                    score_acc -= 20.0
                reasons.append("Sufficient warmth for cool temperature")
            else:
                reasons.append("Comfortable for current weather")

        # Rain check
        if rain_prob and rain_prob > 50:
            for it in items:
                mat = str(it.get("material", "")).lower()
                if "suede" in mat or "canvas" in mat:
                    score_acc -= 30.0
                    reasons.append("⚠ Avoids water-sensitive materials in rain")

        final_score = max(30.0, min(100.0, score_acc))
        main_reason = f"✓ {reasons[0]}" if reasons else "✓ Suitable for weather"
        return final_score, main_reason

class StyleScorer:
    def score(self, items: List[Dict[str, Any]]) -> Tuple[float, str]:
        styles = [it.get("style", "casual").lower() for it in items if it]
        if not styles:
            return 80.0, "✓ Cohesive style"

        unique_styles = set(styles)
        if len(unique_styles) == 1:
            return 100.0, f"✓ Clean single style ({list(unique_styles)[0]})"
        elif len(unique_styles) == 2 and ("casual" in unique_styles or "smart_casual" in unique_styles):
            return 85.0, "✓ Smart casual style blend"
        else:
            return 65.0, "⚠ Mixed style aesthetics"

class FitScorer:
    def score(self, items: List[Dict[str, Any]], preferred_fit: str = "regular") -> Tuple[float, str]:
        if not items:
            return 80.0, "✓ Matches profile fit"
        
        pref = (preferred_fit or "regular").lower()
        matches = 0
        for it in items:
            fit = str(it.get("fit", "regular")).lower()
            if fit == pref or fit == "regular":
                matches += 1
        score_val = (matches / len(items)) * 100.0
        return score_val, "✓ Matches preferred silhouette"

class PreferenceScorer:
    def score(self, items: List[Dict[str, Any]], fav_colors: list, disliked_colors: list, affinity_dict: dict = None) -> Tuple[float, str]:
        fav_colors = [c.lower() for c in (fav_colors or [])]
        disliked_colors = [c.lower() for c in (disliked_colors or [])]
        affinity_dict = affinity_dict or {}

        score_acc = 80.0
        for it in items:
            color = str(it.get("primary_color", "")).lower()
            if color in fav_colors:
                score_acc += 10.0
            if color in disliked_colors:
                score_acc -= 25.0
            
            # Affinity boosts from past user feedback
            color_boost = affinity_dict.get("color_affinity", {}).get(color, 0)
            score_acc += color_boost

        final_score = max(20.0, min(100.0, score_acc))
        reason = "✓ Incorporates your favorite colors & preferences" if final_score >= 85 else "✓ Aligns with user preferences"
        return final_score, reason

class ConditionScorer:
    def score(self, items: List[Dict[str, Any]]) -> Tuple[float, str]:
        if not items:
            return 90.0, "✓ Items in good condition"
        
        scores = []
        for it in items:
            cond = str(it.get("condition", "good")).lower()
            if cond == "new":
                scores.append(100.0)
            elif cond == "good":
                scores.append(90.0)
            elif cond == "worn":
                scores.append(70.0)
            else:
                scores.append(50.0)
        
        avg_score = sum(scores) / len(scores)
        return avg_score, "✓ Items in good condition"

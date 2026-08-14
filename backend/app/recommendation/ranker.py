from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.config import settings
from app.recommendation.scoring.scorers import (
    ColorScorer, OccasionScorer, WeatherScorer, StyleScorer, FitScorer, PreferenceScorer, ConditionScorer
)

class OutfitRanker(ABC):
    @abstractmethod
    def rank(self, candidate_outfits: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ranks candidate outfits given context (weather, occasion, profile, preferences)."""
        pass

class RuleBasedRanker(OutfitRanker):
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or settings.DEFAULT_WEIGHTS
        self.color_scorer = ColorScorer()
        self.occasion_scorer = OccasionScorer()
        self.weather_scorer = WeatherScorer()
        self.style_scorer = StyleScorer()
        self.fit_scorer = FitScorer()
        self.preference_scorer = PreferenceScorer()
        self.condition_scorer = ConditionScorer()

    def rank(self, candidate_outfits: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        occasion = context.get("occasion", "Casual")
        temp_c = context.get("temperature_c", 22.0)
        rain_prob = context.get("rain_probability", 0)
        profile = context.get("profile", {})
        affinity = context.get("user_affinity", {})

        fav_colors = profile.get("favorite_colors", []) if isinstance(profile, dict) else []
        disliked_colors = profile.get("disliked_colors", []) if isinstance(profile, dict) else []
        pref_fit = profile.get("preferred_fit", "regular") if isinstance(profile, dict) else "regular"

        ranked_outfits = []

        for candidate in candidate_outfits:
            raw_items = [it["attribute_dict"] for it in candidate["items"]]

            c_score, c_reason = self.color_scorer.score(raw_items)
            o_score, o_reason = self.occasion_scorer.score(raw_items, occasion)
            w_score, w_reason = self.weather_scorer.score(raw_items, temp_c, rain_prob)
            s_score, s_reason = self.style_scorer.score(raw_items)
            f_score, f_reason = self.fit_scorer.score(raw_items, pref_fit)
            p_score, p_reason = self.preference_scorer.score(raw_items, fav_colors, disliked_colors, affinity)
            cond_score, cond_reason = self.condition_scorer.score(raw_items)

            breakdown = {
                "color": round(c_score, 1),
                "occasion": round(o_score, 1),
                "weather": round(w_score, 1),
                "style": round(s_score, 1),
                "fit": round(f_score, 1),
                "preference": round(p_score, 1),
                "condition": round(cond_score, 1),
            }

            total_score = (
                (c_score * self.weights.get("color", 0.25)) +
                (o_score * self.weights.get("occasion", 0.20)) +
                (w_score * self.weights.get("weather", 0.15)) +
                (s_score * self.weights.get("style", 0.15)) +
                (f_score * self.weights.get("fit", 0.10)) +
                (p_score * self.weights.get("preference", 0.10)) +
                (cond_score * self.weights.get("condition", 0.05))
            )

            reasons = [c_reason, o_reason, w_reason, s_reason, f_reason, p_reason]
            # Keep unique top reasons
            unique_reasons = list(dict.fromkeys(reasons))[:4]

            ranked_outfits.append({
                "candidate": candidate,
                "score": round(total_score, 1),
                "score_breakdown": breakdown,
                "reasons": unique_reasons
            })

        # Sort descending by score
        ranked_outfits.sort(key=lambda x: x["score"], reverse=True)
        return ranked_outfits

class MLRanker(OutfitRanker):
    def __init__(self, model_path: str = None):
        self.fallback = RuleBasedRanker()

    def rank(self, candidate_outfits: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Future ML ranker placeholder - delegates to rule-based ranker
        return self.fallback.rank(candidate_outfits, context)

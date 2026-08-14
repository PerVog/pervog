from typing import Dict, List

COLOR_HARMONY_MATRIX: Dict[str, List[str]] = {
    "white": ["black", "blue", "grey", "beige", "brown", "green", "red", "navy", "olive", "burgundy", "pink", "yellow"],
    "black": ["white", "grey", "blue", "red", "green", "beige", "yellow", "pink", "burgundy"],
    "blue": ["white", "grey", "beige", "black", "brown", "navy", "burgundy"],
    "navy": ["white", "beige", "grey", "pink", "brown", "red", "yellow", "burgundy"],
    "grey": ["white", "black", "blue", "red", "pink", "navy", "burgundy", "green"],
    "beige": ["white", "blue", "navy", "brown", "black", "olive", "burgundy", "green"],
    "brown": ["white", "beige", "blue", "navy", "black", "green"],
    "green": ["white", "black", "beige", "brown", "grey"],
    "olive": ["white", "black", "beige", "navy", "grey", "burgundy"],
    "red": ["white", "black", "navy", "grey", "beige"],
    "burgundy": ["white", "navy", "grey", "beige", "black", "olive"],
    "pink": ["white", "grey", "navy", "black", "beige"],
    "yellow": ["black", "white", "navy", "grey"],
}

NEUTRAL_COLORS = {"white", "black", "grey", "navy", "beige"}

class ColorCompatibilityService:
    @staticmethod
    def get_color_score(primary_color1: str, primary_color2: str) -> float:
        """Returns compatibility score between 0 and 100 for two colors."""
        c1 = primary_color1.lower().strip()
        c2 = primary_color2.lower().strip()

        # Same color (Monochrome)
        if c1 == c2:
            return 90.0 if c1 in NEUTRAL_COLORS else 75.0

        # Neutral + Neutral
        if c1 in NEUTRAL_COLORS and c2 in NEUTRAL_COLORS:
            return 100.0

        # Matrix lookup
        if c1 in COLOR_HARMONY_MATRIX and c2 in COLOR_HARMONY_MATRIX[c1]:
            return 95.0
        if c2 in COLOR_HARMONY_MATRIX and c1 in COLOR_HARMONY_MATRIX[c2]:
            return 95.0

        # Neutral + Any non-neutral
        if c1 in NEUTRAL_COLORS or c2 in NEUTRAL_COLORS:
            return 85.0

        # Clashing fallback
        return 50.0

    @staticmethod
    def evaluate_outfit_colors(colors: List[str]) -> float:
        """Evaluates pairwise color harmony across all items in an outfit."""
        if not colors or len(colors) < 2:
            return 100.0

        valid_colors = [c.lower().strip() for c in colors if c]
        scores = []
        for i in range(len(valid_colors)):
            for j in range(i + 1, len(valid_colors)):
                scores.append(ColorCompatibilityService.get_color_score(valid_colors[i], valid_colors[j]))

        return sum(scores) / len(scores) if scores else 80.0

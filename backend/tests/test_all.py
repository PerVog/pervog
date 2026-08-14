import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database.session import SessionLocal, engine, Base
from app.recommendation.color_rules import ColorCompatibilityService
from app.recommendation.occasion_rules import OccasionService
from app.recommendation.scoring.scorers import ColorScorer, OccasionScorer, WeatherScorer
from app.recommendation.ranker import RuleBasedRanker
from seed.seed_data import seed_database

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"

def test_color_compatibility():
    # White + Black = high compatibility
    score_wb = ColorCompatibilityService.get_color_score("white", "black")
    assert score_wb >= 90.0

    # Blue + Beige = high compatibility
    score_bb = ColorCompatibilityService.get_color_score("blue", "beige")
    assert score_bb >= 90.0

    # Pairwise list check
    outfit_score = ColorCompatibilityService.evaluate_outfit_colors(["white", "blue", "beige"])
    assert outfit_score >= 85.0

def test_occasion_scoring():
    min_f, max_f = OccasionService.get_preferred_formality("interview")
    assert min_f >= 8 and max_f <= 10

    # Formal dress shirt for interview
    formal_score = OccasionService.score_item_for_occasion(9, ["interview"], "interview")
    assert formal_score >= 90.0

    # Casual graphic tee for interview -> lower score
    casual_score = OccasionService.score_item_for_occasion(2, ["casual"], "interview")
    assert casual_score < 60.0

def test_weather_scoring():
    scorer = WeatherScorer()
    # Hot weather (>30°C) with thick sweater (warmth 4) -> penalty
    items_hot = [{"warmth": 4, "material": "wool", "category": "Sweater"}]
    score_hot, reason_hot = scorer.score(items_hot, temp_c=35.0, rain_prob=0)
    assert score_hot < 80.0

    # Hot weather with light cotton tee (warmth 1) -> high score
    items_light = [{"warmth": 1, "material": "cotton", "category": "T-Shirt"}]
    score_light, reason_light = scorer.score(items_light, temp_c=32.0, rain_prob=0)
    assert score_light >= 90.0

def test_wardrobe_api_crud():
    # Fetch wardrobe
    res = client.get("/api/wardrobe?user_id=1")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 20

    # Filter category = Shirt
    res_shirts = client.get("/api/wardrobe?user_id=1&category=Shirt")
    assert res_shirts.status_code == 200
    shirts = res_shirts.json()
    assert all(it["category"] == "Shirt" for it in shirts)

def test_recommendation_api():
    req_body = {
        "user_id": 1,
        "occasion": "Casual Outing",
        "manual_temperature_c": 24.0,
        "limit": 3
    }
    res = client.post("/api/recommendations", json=req_body)
    assert res.status_code == 200
    outfits = res.json()
    assert len(outfits) > 0
    top_outfit = outfits[0]
    assert top_outfit["score"] > 50.0
    assert len(top_outfit["items"]) >= 3

def test_select_item_recommendation_api():
    # Pick first item ID
    res_items = client.get("/api/wardrobe?user_id=1")
    first_item_id = res_items.json()[0]["id"]

    res = client.post(f"/api/recommendations/item/{first_item_id}?user_id=1&occasion=Casual%20Outing")
    assert res.status_code == 200
    outfits = res.json()
    assert len(outfits) > 0
    # Check that selected item is in the recommended outfit items
    top_items = outfits[0]["items"]
    assert any(it["item"]["id"] == first_item_id for it in top_items)

def test_feedback_api():
    req_body = {
        "user_id": 1,
        "outfit_id": 1,
        "liked": True,
        "saved": True,
        "rating": 5
    }
    res = client.post("/api/outfits/feedback", json=req_body)
    assert res.status_code == 200
    fb = res.json()
    assert fb["liked"] is True

def test_shopping_gaps_api():
    res = client.get("/api/shopping/recommendations?user_id=1")
    assert res.status_code == 200
    gaps = res.json()
    assert "missing_gaps" in gaps
    assert len(gaps["missing_gaps"]) > 0

def test_weather_api():
    res = client.get("/api/weather?location=New%20York")
    assert res.status_code == 200
    w = res.json()
    assert "temperature_c" in w
    assert "advice" in w

def test_hsv_color_classification():
    from app.ai.providers.local_vision_provider import classify_hsv_color_kmeans, rgb_to_hsv
    
    # Pure white
    name, hex_c = classify_hsv_color_kmeans((250, 252, 255))
    assert name == "white"

    # Navy Blue
    name, hex_c = classify_hsv_color_kmeans((15, 30, 80))
    assert name in ["navy", "dark navy", "black"]


    # Green
    name, hex_c = classify_hsv_color_kmeans((30, 150, 60))
    assert name == "green"

def test_batch_wardrobe_api():
    batch_data = [
        {
            "title": "Batch Test Glasses",
            "category": "Glasses",
            "image_url": "/uploads/test_g.jpg",
            "attributes": {"primary_color": "black", "style": "casual", "formality": 3}
        },
        {
            "title": "Batch Test Watch",
            "category": "Watch",
            "image_url": "/uploads/test_w.jpg",
            "attributes": {"primary_color": "brown", "style": "casual", "formality": 4}
        }
    ]
    res = client.post("/api/wardrobe/batch?user_id=1", json=batch_data)
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 2
    assert items[0]["category"] == "Glasses"

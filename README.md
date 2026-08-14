# AURA — AI Personal Stylist & Wardrobe Assistant

> **Zero Paid Dependencies (₹0 Budget)** full-stack digital wardrobe manager, deterministic outfit recommendation engine, weather integration, and wardrobe gap analyzer.

---

## 🌟 Features Overview

1. **Digital Wardrobe Management**: Upload, view, edit, search, filter, and track availability/favorites for your clothes.
2. **Local AI Vision Analysis**: Automatic image processing using Pillow & K-Means RGB dominant color extraction to suggest colors and attributes without paid APIs.
3. **Deterministic Recommendation Engine**: Rule-based combinatorial outfit ranking algorithm balancing:
   - **Color Compatibility (25%)**: Pairwise harmony matrix (monochrome, neutrals, complementary rules).
   - **Occasion Suitability (20%)**: Formality matching (Interview 8-10, College 2-5, Wedding 7-10, etc.).
   - **Weather Comfort (15%)**: Temperature threshold & rain material avoidance (Open-Meteo free API).
   - **Style Coherence (15%)**: Aesthetic consistency (casual, smart casual, streetwear, athletic, formal).
   - **Profile & Fit Fit (10%)**: Height, weight, preferred silhouette matching.
   - **Personal Preferences (10%)**: Favorite color boosts & feedback affinity.
   - **Item Condition (5%)**: Condition scoring.
4. **"Match an Item" Feature**: Pick any anchor piece (e.g. Dark Blue Jeans) to generate complete styled outfits built around it with score cards and rationale ("Why this works").
5. **Wardrobe Gap & Shopping Recommendations**: Calculates missing essential staples (e.g. White Sneakers, Denim Jacket) and outfit potential multipliers unlocked with your current closet.
6. **User Feedback & Personalization**: Record Likes, Dislikes, Worn status, and Ratings to update preference feature weights dynamically over time.

---

## 🏗️ Architecture

```text
Frontend (React + Vite + Modern Glass CSS)
    │
    ▼
Backend API (FastAPI + Pydantic + SQLAlchemy)
    │
    ├── Database (SQLite dev / PostgreSQL ready)
    ├── Local Image Storage (`uploads/`)
    ├── Weather Service (Free Open-Meteo API)
    ├── Clothing Analyzer (PIL / OpenCV local vision)
    ├── Recommendation Engine (Combinatorial Outfit Generator)
    └── Outfit Ranker (`RuleBasedRanker` -> `MLRanker` extensible interface)
```

---

## 🚀 Quickstart Guide (Zero API Keys Required)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create & activate virtual environment (optional)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install free dependencies
pip install -r requirements.txt

# Seed 65 initial wardrobe items with generated images
python seed/seed_data.py

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

FastAPI OpenAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install npm packages
npm install

# Start Vite development server
npm run dev
```

Frontend application running at: [http://localhost:3000](http://localhost:3000)

---

## 🧪 Automated Testing

To run the automated backend test suite:

```bash
cd backend
pytest -v
```

Tests cover:
- Database creation & User profile updates
- Wardrobe CRUD & filtering APIs
- Pairwise color harmony calculations
- Occasion formality range matching
- Temperature & rain weather rules
- Outfit recommendation generation & Select-Item matching
- Feedback recording & preference adjustments
- Shopping gap analysis

---

## 📊 Database Schema Overview

- **users**: `id`, `name`, `email`, `created_at`
- **user_profiles**: `user_id`, `age`, `gender_preference`, `height_cm`, `weight_kg`, `skin_tone`, `preferred_fit`, `favorite_colors`, `disliked_colors`, `location`
- **wardrobe_items**: `id`, `user_id`, `title`, `category`, `image_url`, `is_favorite`, `is_available`
- **wardrobe_item_attributes**: `item_id`, `primary_color`, `color_hex`, `pattern`, `material`, `fit`, `style`, `formality`, `warmth`, `occasions`, `condition`
- **outfits**: `id`, `user_id`, `title`, `occasion`, `weather_condition`, `temperature_c`, `score`, `score_breakdown`, `reasons`
- **outfit_items**: `outfit_id`, `item_id`, `role`
- **outfit_feedback**: `user_id`, `outfit_id`, `liked`, `saved`, `worn`, `rating`
- **user_preferences**: `user_id`, `color_affinity`, `style_affinity`
- **weather_cache**: `location`, `temperature_c`, `rain_probability`, `weather_condition`, `fetched_at`

---

## 🛡️ Zero Paid Dependencies Audit

1. **AI Vision:** 100% Offline / Local K-Means RGB & Rule-Based Heuristic Classifiers
2. **Weather API:** Free Open-Meteo API (Zero API key required)
3. **Database:** SQLite with SQLAlchemy (PostgreSQL production-ready)
4. **Image Storage:** Local Filesystem (`uploads/` directory) with S3/R2 abstraction layer
5. **Recommendation Engine:** Weighted Rule-Based Deterministic Matrix

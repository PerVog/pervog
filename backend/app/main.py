import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database.session import engine, Base, SessionLocal
from app.models.user import User, UserProfile
from app.models.preference import UserPreference
from app.api.routes import users, wardrobe, recommendations, feedback, shopping, weather, ai

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-stack AI Personal Stylist with multi-model computer vision clothing analysis.",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount local image uploads & storage directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
storage_dir = os.path.join(os.getcwd(), "storage")
crops_dir = os.path.join(storage_dir, "crops")
os.makedirs(crops_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/storage", StaticFiles(directory=storage_dir), name="storage")

# Include Routers
app.include_router(users.router, prefix="/api")
app.include_router(wardrobe.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(shopping.router, prefix="/api")
app.include_router(weather.router, prefix="/api")
app.include_router(ai.router, prefix="/api")

@app.on_event("startup")
def startup_event():
    # Create default demo user if not exists
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            user = User(id=1, name="Alex Stylist", email="alex@example.com")
            db.add(user)
            db.flush()
            profile = UserProfile(
                user_id=1,
                age=26,
                gender_preference="all",
                height_cm=178.0,
                weight_kg=72.0,
                skin_tone="medium",
                preferred_fit="regular",
                preferred_styles=["casual", "smart_casual", "minimalist"],
                favorite_colors=["white", "blue", "navy", "grey", "black"],
                disliked_colors=["neon green"],
                location="New York"
            )
            pref = UserPreference(user_id=1, color_affinity={}, style_affinity={})
            db.add(profile)
            db.add(pref)
            db.commit()
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "docs_url": "/docs",
        "ai_provider": settings.AI_PROVIDER
    }

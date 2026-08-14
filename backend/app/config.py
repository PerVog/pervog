import os
from pydantic_settings import BaseSettings
from typing import Dict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Personal Stylist"
    DATABASE_URL: str = "sqlite:///./stylist.db"
    STORAGE_TYPE: str = "local"
    UPLOAD_DIR: str = "uploads"
    AI_PROVIDER: str = "local"  # "manual" or "local"
    LOG_LEVEL: str = "INFO"
    
    # Weather API (Free Open-Meteo)
    WEATHER_API_URL: str = "https://api.open-meteo.com/v1/forecast"
    GEOCODING_API_URL: str = "https://geocoding-api.open-meteo.com/v1/search"

    # Configurable Recommendation Engine Weights
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "color": 0.25,
        "occasion": 0.20,
        "weather": 0.15,
        "style": 0.15,
        "fit": 0.10,
        "preference": 0.10,
        "condition": 0.05
    }

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

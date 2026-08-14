from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database.session import Base

class WeatherCache(Base):
    __tablename__ = "weather_cache"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, unique=True, index=True, nullable=False)
    temperature_c = Column(Float, nullable=False)
    feels_like_c = Column(Float, nullable=False)
    humidity = Column(Integer, nullable=False)
    rain_probability = Column(Integer, nullable=False)
    wind_speed_kmh = Column(Float, nullable=False)
    weather_condition = Column(String, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)

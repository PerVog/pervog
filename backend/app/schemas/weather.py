from pydantic import BaseModel
from typing import Optional

class WeatherResponse(BaseModel):
    location: str
    temperature_c: float
    feels_like_c: float
    humidity: int
    rain_probability: int
    wind_speed_kmh: float
    weather_condition: str
    advice: Optional[str] = None

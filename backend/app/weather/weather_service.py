import requests
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.config import settings
from app.models.weather import WeatherCache
from app.schemas.weather import WeatherResponse

class WeatherService:
    def __init__(self, db: Session = None):
        self.db = db

    def get_weather(self, location: str = "New York") -> WeatherResponse:
        """Fetch weather for location using Open-Meteo free API with local cache fallback."""
        location_norm = location.strip().capitalize() if location else "New York"
        
        # 1. Check local cache (fresh if fetched within 30 minutes)
        if self.db:
            cached = self.db.query(WeatherCache).filter(WeatherCache.location == location_norm).first()
            if cached and (datetime.utcnow() - cached.fetched_at) < timedelta(minutes=30):
                return self._cache_to_schema(cached)

        # 2. Geocode location to lat/lon using Open-Meteo Geocoding
        lat, lon = 40.7128, -74.0060 # Default NYC
        try:
            geo_res = requests.get(
                settings.GEOCODING_API_URL,
                params={"name": location_norm, "count": 1},
                timeout=4
            )
            if geo_res.status_code == 200:
                geo_data = geo_res.json()
                if geo_data.get("results"):
                    lat = geo_data["results"][0]["latitude"]
                    lon = geo_data["results"][0]["longitude"]
        except Exception:
            pass # Fallback to defaults

        # 3. Fetch Forecast from Open-Meteo
        temp_c = 22.0
        feels_c = 22.0
        humidity = 55
        rain_prob = 10
        wind = 12.0
        condition = "Clear / Sunny"

        try:
            weather_res = requests.get(
                settings.WEATHER_API_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"
                },
                timeout=4
            )
            if weather_res.status_code == 200:
                w_data = weather_res.json().get("current", {})
                temp_c = w_data.get("temperature_2m", 22.0)
                feels_c = w_data.get("apparent_temperature", temp_c)
                humidity = w_data.get("relative_humidity_2m", 55)
                rain_prob = 80 if w_data.get("precipitation", 0) > 0.5 else 10
                wind = w_data.get("wind_speed_10m", 12.0)
                
                code = w_data.get("weather_code", 0)
                if code in [1, 2, 3]:
                    condition = "Partly Cloudy"
                elif code in [45, 48]:
                    condition = "Foggy"
                elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                    condition = "Rainy"
                elif code >= 71:
                    condition = "Snowy"
                else:
                    condition = "Sunny & Clear"
        except Exception:
            pass

        # 4. Generate human advice snippet based on temp/rain
        advice = self._generate_advice(temp_c, rain_prob)

        res_schema = WeatherResponse(
            location=location_norm,
            temperature_c=round(temp_c, 1),
            feels_like_c=round(feels_c, 1),
            humidity=humidity,
            rain_probability=rain_prob,
            wind_speed_kmh=round(wind, 1),
            weather_condition=condition,
            advice=advice
        )

        # 5. Save/Update DB Cache
        if self.db:
            try:
                cached = self.db.query(WeatherCache).filter(WeatherCache.location == location_norm).first()
                if not cached:
                    cached = WeatherCache(location=location_norm)
                    self.db.add(cached)
                
                cached.temperature_c = temp_c
                cached.feels_like_c = feels_c
                cached.humidity = humidity
                cached.rain_probability = rain_prob
                cached.wind_speed_kmh = wind
                cached.weather_condition = condition
                cached.fetched_at = datetime.utcnow()
                self.db.commit()
            except Exception:
                self.db.rollback()

        return res_schema

    def _generate_advice(self, temp_c: float, rain_prob: int) -> str:
        advice_parts = []
        if temp_c > 30:
            advice_parts.append("Hot weather: prefer light cotton, linen, and short sleeves.")
        elif temp_c < 15:
            advice_parts.append("Cool weather: layered clothing, sweater, or lightweight jacket recommended.")
        elif temp_c < 5:
            advice_parts.append("Cold weather: heavy coat, thermal layer, and boots recommended.")
        else:
            advice_parts.append("Mild pleasant temperature: versatile layering works great.")

        if rain_prob > 50:
            advice_parts.append("High chance of rain: avoid suede shoes and delicate fabrics.")

        return " ".join(advice_parts)

    def _cache_to_schema(self, cached: WeatherCache) -> WeatherResponse:
        advice = self._generate_advice(cached.temperature_c, cached.rain_probability)
        return WeatherResponse(
            location=cached.location,
            temperature_c=cached.temperature_c,
            feels_like_c=cached.feels_like_c,
            humidity=cached.humidity,
            rain_probability=cached.rain_probability,
            wind_speed_kmh=cached.wind_speed_kmh,
            weather_condition=cached.weather_condition,
            advice=advice
        )

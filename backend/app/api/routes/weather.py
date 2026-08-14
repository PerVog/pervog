from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.weather import WeatherResponse
from app.weather.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("", response_model=WeatherResponse)
def get_weather(location: str = Query("New York"), db: Session = Depends(get_db)):
    service = WeatherService(db)
    return service.get_weather(location)

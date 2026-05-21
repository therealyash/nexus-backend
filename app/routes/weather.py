from fastapi import APIRouter, Depends

from app.controllers.weather_controller import WeatherController
from app.dependencies import get_weather_controller

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("")
async def get_weather(ctrl: WeatherController = Depends(get_weather_controller)):
    return await ctrl.get_readings()

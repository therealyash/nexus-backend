from fastapi import HTTPException

from app.services.weather_service import WeatherService


class WeatherController:
    def __init__(self, svc: WeatherService):
        self._svc = svc

    async def get_readings(self) -> list:
        try:
            return await self._svc.get_readings()
        except RuntimeError as e:
            raise HTTPException(502, str(e))

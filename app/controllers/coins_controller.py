from fastapi import HTTPException

from app.services.coins_service import CoinsService


class CoinsController:
    def __init__(self, svc: CoinsService):
        self._svc = svc

    async def get_all(self) -> list:
        try:
            return await self._svc.get_all()
        except RuntimeError as e:
            raise HTTPException(502, str(e))

    async def get_one(self, symbol: str) -> dict:
        try:
            return await self._svc.get_one(symbol)
        except ValueError as e:
            raise HTTPException(404, str(e))
        except RuntimeError as e:
            raise HTTPException(502, str(e))

    async def get_chart(self, symbol: str, interval: str, limit: int) -> list:
        try:
            return await self._svc.get_chart(symbol, interval, limit)
        except ValueError as e:
            raise HTTPException(404, str(e))
        except RuntimeError as e:
            raise HTTPException(502, str(e))

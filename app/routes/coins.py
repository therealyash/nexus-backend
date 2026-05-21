from fastapi import APIRouter, Depends

from app.controllers.coins_controller import CoinsController
from app.dependencies import get_coins_controller

router = APIRouter(prefix="/coins", tags=["Coins"])


@router.get("")
async def get_all_coins(ctrl: CoinsController = Depends(get_coins_controller)):
    return await ctrl.get_all()


@router.get("/{symbol}/chart")
async def get_coin_chart(
    symbol: str,
    interval: str = "1h",
    limit: int = 24,
    ctrl: CoinsController = Depends(get_coins_controller),
):
    return await ctrl.get_chart(symbol, interval, limit)


@router.get("/{symbol}")
async def get_coin(symbol: str, ctrl: CoinsController = Depends(get_coins_controller)):
    return await ctrl.get_one(symbol)

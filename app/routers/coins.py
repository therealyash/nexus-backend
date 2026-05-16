from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(prefix="/coins", tags=["Coins"])

BINANCE_BASE = "https://api.binance.com/api/v3/ticker/24hr"


@router.get("")
async def get_all_coins():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(BINANCE_BASE)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Could not reach Binance API")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Could not reach Binance API")
    return [
        {
            "symbol": c["symbol"],
            "lastPrice": c["lastPrice"],
            "priceChangePercent": c["priceChangePercent"],
            "trend": "UP" if float(c["priceChangePercent"]) >= 0 else "DOWN",
        }
        for c in response.json()
    ]


@router.get("/{symbol}/chart")
async def get_coin_chart(symbol: str, interval: str = "1h", limit: int = 24):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.binance.com/api/v3/klines",
                params={"symbol": symbol.upper(), "interval": interval, "limit": limit},
            )
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Could not reach Binance API")
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail=f"No chart data for {symbol}")
    return [
        {"time": k[0], "open": float(k[1]), "high": float(k[2]), "low": float(k[3]), "close": float(k[4]), "volume": float(k[5])}
        for k in response.json()
    ]


@router.get("/{symbol}")
async def get_coin(symbol: str):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(BINANCE_BASE, params={"symbol": symbol.upper()})
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Could not reach Binance API")
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail=f"Coin {symbol} not found")
    c = response.json()
    return {
        "symbol": c["symbol"],
        "lastPrice": c["lastPrice"],
        "priceChangePercent": c["priceChangePercent"],
        "highPrice": c["highPrice"],
        "lowPrice": c["lowPrice"],
        "volume": c["volume"],
        "trend": "UP" if float(c["priceChangePercent"]) >= 0 else "DOWN",
    }

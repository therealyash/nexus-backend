import httpx

_BINANCE_BASE = "https://api.binance.com/api/v3"


class CoinsService:
    async def get_all(self) -> list:
        data = await self._fetch(f"{_BINANCE_BASE}/ticker/24hr")
        return [self._format_ticker(c) for c in data]

    async def get_one(self, symbol: str) -> dict:
        data = await self._fetch(f"{_BINANCE_BASE}/ticker/24hr", {"symbol": symbol.upper()})
        return {
            **self._format_ticker(data),
            "highPrice": data["highPrice"],
            "lowPrice": data["lowPrice"],
            "volume": data["volume"],
        }

    async def get_chart(self, symbol: str, interval: str, limit: int) -> list:
        data = await self._fetch(
            f"{_BINANCE_BASE}/klines",
            {"symbol": symbol.upper(), "interval": interval, "limit": limit},
        )
        return [
            {
                "time": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
            }
            for k in data
        ]

    @staticmethod
    def _format_ticker(c: dict) -> dict:
        return {
            "symbol": c["symbol"],
            "lastPrice": c["lastPrice"],
            "priceChangePercent": c["priceChangePercent"],
            "trend": "UP" if float(c["priceChangePercent"]) >= 0 else "DOWN",
        }

    @staticmethod
    async def _fetch(url: str, params: dict = None):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, params=params)
        except httpx.RequestError:
            raise RuntimeError("Could not reach Binance API")
        if resp.status_code != 200:
            raise ValueError(f"Binance returned {resp.status_code} for {url}")
        return resp.json()

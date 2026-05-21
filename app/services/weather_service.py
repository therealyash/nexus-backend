import httpx

_WEATHER_URL = "https://api.data.gov.sg/v1/environment/air-temperature"


class WeatherService:
    async def get_readings(self) -> list:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(_WEATHER_URL)
        except httpx.RequestError:
            raise RuntimeError("Could not reach Weather API")
        if resp.status_code != 200:
            raise RuntimeError("Weather API returned an error")

        data = resp.json()
        stations = {s["id"]: s["name"] for s in data["metadata"]["stations"]}
        return [
            {
                "station": stations.get(r["station_id"], r["station_id"]),
                "temperature_c": r["value"],
            }
            for r in data["items"][0]["readings"]
        ]

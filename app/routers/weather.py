from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("")
async def get_weather():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.data.gov.sg/v1/environment/air-temperature")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Could not reach Weather API")
    data = response.json()
    stations = {s["id"]: s["name"] for s in data["metadata"]["stations"]}
    readings = data["items"][0]["readings"]
    return [
        {"station": stations.get(r["station_id"], r["station_id"]), "temperature_c": r["value"]}
        for r in readings
    ]

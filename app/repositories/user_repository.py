from typing import Optional
from motor.motor_asyncio import AsyncIOMotorCollection

from .base import IUserRepository


class MongoUserRepository(IUserRepository):
    def __init__(self, col: AsyncIOMotorCollection):
        self._col = col

    async def find_by_email(self, email: str) -> Optional[dict]:
        return await self._col.find_one({"email": email})

    async def create(self, data: dict) -> None:
        await self._col.insert_one(data)

    async def update_by_email(self, email: str, updates: dict) -> None:
        await self._col.update_one({"email": email}, {"$set": updates})

    async def exists_by_email(self, email: str) -> bool:
        return await self._col.find_one({"email": email}, {"_id": 1}) is not None

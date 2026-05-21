from abc import ABC, abstractmethod
from typing import Optional


class IUserRepository(ABC):
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[dict]: ...

    @abstractmethod
    async def create(self, data: dict) -> None: ...

    @abstractmethod
    async def update_by_email(self, email: str, updates: dict) -> None: ...

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool: ...

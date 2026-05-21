from typing import Optional

from fastapi import HTTPException

from app.models.user import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


class AuthController:
    def __init__(self, svc: AuthService):
        self._svc = svc

    async def register(self, body: RegisterRequest) -> dict:
        try:
            await self._svc.register(body.name, body.email, body.password)
            return {"message": "Registered successfully"}
        except ValueError as e:
            raise HTTPException(400, str(e))

    async def login(self, body: LoginRequest) -> dict:
        try:
            token = await self._svc.login(body.email, body.password)
            return {"access_token": token, "token_type": "bearer"}
        except ValueError as e:
            raise HTTPException(400, str(e))

    def logout(self, authorization: Optional[str]) -> dict:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(401, "No token provided")
        self._svc.blacklist_token(authorization.split(" ")[1])
        return {"message": "Logged out successfully"}

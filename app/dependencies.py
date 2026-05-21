from typing import Optional

from fastapi import Depends, Header, HTTPException

from app.controllers.auth_controller import AuthController
from app.controllers.coins_controller import CoinsController
from app.controllers.user_controller import UserController
from app.controllers.weather_controller import WeatherController
from app.database import users_col
from app.repositories.base import IUserRepository
from app.repositories.user_repository import MongoUserRepository
from app.services.auth_service import AuthService
from app.services.coins_service import CoinsService
from app.services.user_service import UserService
from app.services.weather_service import WeatherService


# ── Repository providers ──────────────────────────────────────────────────────

def get_user_repo() -> IUserRepository:
    return MongoUserRepository(users_col)


# ── Service providers ─────────────────────────────────────────────────────────

def get_auth_service(repo: IUserRepository = Depends(get_user_repo)) -> AuthService:
    return AuthService(repo)


def get_user_service(repo: IUserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(repo)


# ── Controller providers ──────────────────────────────────────────────────────

def get_auth_controller(svc: AuthService = Depends(get_auth_service)) -> AuthController:
    return AuthController(svc)


def get_user_controller(svc: UserService = Depends(get_user_service)) -> UserController:
    return UserController(svc)


def get_coins_controller() -> CoinsController:
    return CoinsController(CoinsService())


def get_weather_controller() -> WeatherController:
    return WeatherController(WeatherService())


# ── Auth dependency for protected routes ─────────────────────────────────────

async def get_current_user(
    authorization: Optional[str] = Header(None),
    auth_svc: AuthService = Depends(get_auth_service),
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or bad Authorization header")
    token = authorization.split(" ")[1]
    try:
        return await auth_svc.authenticate_token(token)
    except ValueError as e:
        raise HTTPException(401, str(e))

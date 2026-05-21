from typing import Optional

from fastapi import APIRouter, Depends, Header

from app.controllers.auth_controller import AuthController
from app.dependencies import get_auth_controller
from app.models.user import LoginRequest, RegisterRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(body: RegisterRequest, ctrl: AuthController = Depends(get_auth_controller)):
    return await ctrl.register(body)


@router.post("/login")
async def login(body: LoginRequest, ctrl: AuthController = Depends(get_auth_controller)):
    return await ctrl.login(body)


@router.get("/google")
def google_login(ctrl: AuthController = Depends(get_auth_controller)):
    return ctrl.get_google_url()


@router.get("/google/callback")
async def google_callback(code: str, ctrl: AuthController = Depends(get_auth_controller)):
    return await ctrl.google_callback(code)


@router.post("/logout")
def logout(
    authorization: Optional[str] = Header(None),
    ctrl: AuthController = Depends(get_auth_controller),
):
    return ctrl.logout(authorization)

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.controllers.user_controller import UserController
from app.dependencies import get_current_user, get_user_controller
from app.models.user import UpdateProfileRequest

router = APIRouter(prefix="/users", tags=["Profile"])


@router.get("/profile")
async def get_profile(
    email: str = Depends(get_current_user),
    ctrl: UserController = Depends(get_user_controller),
):
    return await ctrl.get_profile(email)


@router.put("/profile")
async def update_profile(
    body: UpdateProfileRequest,
    email: str = Depends(get_current_user),
    ctrl: UserController = Depends(get_user_controller),
):
    return await ctrl.update_profile(email, body)


@router.post("/photo")
async def upload_photo(
    email: str = Depends(get_current_user),
    ctrl: UserController = Depends(get_user_controller),
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
):
    return await ctrl.upload_photo(email, file, image_url)

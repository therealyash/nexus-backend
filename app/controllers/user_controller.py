from typing import Optional

from fastapi import HTTPException, UploadFile

from app.models.user import UpdateProfileRequest
from app.services.user_service import UserService


class UserController:
    def __init__(self, svc: UserService):
        self._svc = svc

    async def get_profile(self, email: str) -> dict:
        try:
            return await self._svc.get_profile(email)
        except ValueError as e:
            raise HTTPException(404, str(e))

    async def update_profile(self, email: str, body: UpdateProfileRequest) -> dict:
        try:
            profile = await self._svc.update_profile(email, body.model_dump(exclude_none=True))
            return {"message": "Profile updated", "profile": profile}
        except ValueError as e:
            raise HTTPException(400, str(e))

    async def upload_photo(
        self, email: str, file: Optional[UploadFile], image_url: Optional[str]
    ) -> dict:
        file_contents = await file.read() if file else None
        try:
            photo = await self._svc.set_photo(email, image_url, file_contents)
            return {"message": "Photo updated", "photo": photo}
        except ValueError as e:
            raise HTTPException(400, str(e))

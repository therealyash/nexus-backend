from typing import Optional

import bcrypt
import cloudinary
import cloudinary.uploader

from app.config import CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, CLOUDINARY_CLOUD_NAME
from app.repositories.base import IUserRepository

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)

_SAFE_FIELDS = frozenset({"name", "email", "bio", "phone", "photo"})


class UserService:
    def __init__(self, repo: IUserRepository):
        self._repo = repo

    @staticmethod
    def _to_profile(user: dict) -> dict:
        return {k: v for k, v in user.items() if k in _SAFE_FIELDS}

    async def get_profile(self, email: str) -> dict:
        user = await self._repo.find_by_email(email)
        if not user:
            raise ValueError("User not found")
        return self._to_profile(user)

    async def update_profile(self, email: str, updates: dict) -> dict:
        db_updates: dict = {}

        for field in ("name", "bio", "phone"):
            if field in updates and updates[field] is not None:
                db_updates[field] = updates[field]

        if updates.get("password"):
            db_updates["password_hash"] = bcrypt.hashpw(
                updates["password"].encode(), bcrypt.gensalt()
            ).decode()

        new_email = updates.get("email")
        if new_email and new_email != email:
            if await self._repo.exists_by_email(new_email):
                raise ValueError("New email already in use")
            db_updates["email"] = new_email

        if db_updates:
            await self._repo.update_by_email(email, db_updates)

        current_email = db_updates.get("email", email)
        user = await self._repo.find_by_email(current_email)
        return self._to_profile(user)

    async def set_photo(
        self, email: str, photo_url: Optional[str], file_contents: Optional[bytes]
    ) -> str:
        if file_contents:
            result = cloudinary.uploader.upload(
                file_contents,
                folder="nexus/avatars",
                public_id=email.replace("@", "_").replace(".", "_"),
                overwrite=True,
                resource_type="image",
            )
            photo = result["secure_url"]
        elif photo_url:
            photo = photo_url
        else:
            raise ValueError("Provide either a file or image_url")

        await self._repo.update_by_email(email, {"photo": photo})
        return photo

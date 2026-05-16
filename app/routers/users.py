from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional
import bcrypt
import cloudinary
import cloudinary.uploader

from app.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
from app.database import users_col
from app.dependencies import get_current_user
from app.models.user import UpdateProfileRequest

router = APIRouter(prefix="/users", tags=["Profile"])

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)


@router.get("/profile")
async def get_profile(email: str = Depends(get_current_user)):
    user = await users_col.find_one({"email": email}, {"_id": 0, "password_hash": 0})
    return user


@router.put("/profile")
async def update_profile(body: UpdateProfileRequest, email: str = Depends(get_current_user)):
    updates: dict = {}
    if body.name:  updates["name"]  = body.name
    if body.bio:   updates["bio"]   = body.bio
    if body.phone: updates["phone"] = body.phone
    if body.password:
        updates["password_hash"] = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()

    if body.email and body.email != email:
        if await users_col.find_one({"email": body.email}):
            raise HTTPException(status_code=400, detail="New email already in use")
        updates["email"] = body.email

    if updates:
        await users_col.update_one({"email": email}, {"$set": updates})

    new_email = updates.get("email", email)
    updated = await users_col.find_one({"email": new_email}, {"_id": 0, "password_hash": 0})
    return {"message": "Profile updated", "profile": updated}


@router.post("/photo")
async def upload_photo(
    email: str = Depends(get_current_user),
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
):
    if file:
        contents = await file.read()
        result = cloudinary.uploader.upload(
            contents,
            folder="nexus/avatars",
            public_id=email.replace("@", "_").replace(".", "_"),
            overwrite=True,
            resource_type="image",
        )
        photo = result["secure_url"]
    elif image_url:
        photo = image_url
    else:
        raise HTTPException(status_code=400, detail="Provide either a file or image_url")

    await users_col.update_one({"email": email}, {"$set": {"photo": photo}})
    return {"message": "Photo updated", "photo": photo}

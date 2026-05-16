from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
import httpx

from app.config import SECRET_KEY, ALGORITHM, TOKEN_EXPIRY_HOURS, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
from app.database import users_col, BLACKLIST
from app.models.user import RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


def create_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register")
async def register(body: RegisterRequest):
    if await users_col.find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    await users_col.insert_one({
        "name": body.name,
        "email": body.email,
        "password_hash": hashed_pw,
        "bio": "",
        "phone": "",
        "photo": "",
    })
    return {"message": "Registered successfully"}


@router.post("/login")
async def login(body: LoginRequest):
    user = await users_col.find_one({"email": body.email})
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if not bcrypt.checkpw(body.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=400, detail="Wrong password")
    token = create_token(body.email)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/google")
def google_login():
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile"
    )
    return {"google_auth_url": url}


@router.get("/google/callback")
async def google_callback(code: str):
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        access_token = token_resp.json().get("access_token")
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        google_user = user_resp.json()

    email = google_user.get("email")
    name = google_user.get("name", "")
    photo = google_user.get("picture", "")

    if not await users_col.find_one({"email": email}):
        await users_col.insert_one({
            "name": name,
            "email": email,
            "password_hash": "",
            "bio": "",
            "phone": "",
            "photo": photo,
        })

    token = create_token(email)
    return {"access_token": token, "token_type": "bearer", "name": name}


@router.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    BLACKLIST.add(authorization.split(" ")[1])
    return {"message": "Logged out successfully"}

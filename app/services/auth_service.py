from datetime import datetime, timedelta

import bcrypt
import httpx
import jwt

from app.config import (
    ALGORITHM,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    SECRET_KEY,
    TOKEN_EXPIRY_HOURS,
)
from app.repositories.base import IUserRepository

# Module-level blacklist — sufficient for a single-process deployment where
# tokens expire after TOKEN_EXPIRY_HOURS anyway.
_BLACKLIST: set[str] = set()


class AuthService:
    def __init__(self, repo: IUserRepository):
        self._repo = repo

    # ── Token management ──────────────────────────────────────────────────────

    def create_token(self, email: str) -> str:
        payload = {
            "sub": email,
            "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> str:
        if token in _BLACKLIST:
            raise ValueError("Token has been revoked")
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    def blacklist_token(self, token: str) -> None:
        _BLACKLIST.add(token)

    # ── Password helpers ──────────────────────────────────────────────────────

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    # ── Auth flows ────────────────────────────────────────────────────────────

    async def register(self, name: str, email: str, password: str) -> None:
        if await self._repo.exists_by_email(email):
            raise ValueError("Email already registered")
        await self._repo.create({
            "name": name,
            "email": email,
            "password_hash": self.hash_password(password),
            "bio": "",
            "phone": "",
            "photo": "",
        })

    async def login(self, email: str, password: str) -> str:
        user = await self._repo.find_by_email(email)
        if not user:
            raise ValueError("User not found")
        if not self.verify_password(password, user["password_hash"]):
            raise ValueError("Wrong password")
        return self.create_token(email)

    def get_google_auth_url(self) -> str:
        return (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={GOOGLE_CLIENT_ID}"
            f"&redirect_uri={GOOGLE_REDIRECT_URI}"
            "&response_type=code"
            "&scope=openid email profile"
        )

    async def google_callback(self, code: str) -> dict:
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

        if not await self._repo.exists_by_email(email):
            await self._repo.create({
                "name": name,
                "email": email,
                "password_hash": "",
                "bio": "",
                "phone": "",
                "photo": photo,
            })

        return {"token": self.create_token(email), "name": name}

    async def authenticate_token(self, token: str) -> str:
        """Verify the token is valid and the user still exists. Returns email."""
        email = self.verify_token(token)
        if not await self._repo.exists_by_email(email):
            raise ValueError("User not found")
        return email

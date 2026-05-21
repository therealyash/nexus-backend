import os
from datetime import datetime, timedelta

import bcrypt
import jwt

from app.repositories.base import IUserRepository

_SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
_ALGORITHM = "HS256"
_TOKEN_EXPIRY_HOURS = int(os.getenv("TOKEN_EXPIRY_HOURS", "24"))

# Module-level blacklist — sufficient for a single-process deployment where
# tokens expire after _TOKEN_EXPIRY_HOURS anyway.
_BLACKLIST: set[str] = set()


class AuthService:
    def __init__(self, repo: IUserRepository):
        self._repo = repo

    # ── Token management ──────────────────────────────────────────────────────

    def create_token(self, email: str) -> str:
        payload = {
            "sub": email,
            "exp": datetime.utcnow() + timedelta(hours=_TOKEN_EXPIRY_HOURS),
        }
        return jwt.encode(payload, _SECRET_KEY, algorithm=_ALGORITHM)

    def verify_token(self, token: str) -> str:
        if token in _BLACKLIST:
            raise ValueError("Token has been revoked")
        try:
            return jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])["sub"]
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

    async def authenticate_token(self, token: str) -> str:
        """Verify the token is valid and the user still exists. Returns email."""
        email = self.verify_token(token)
        if not await self._repo.exists_by_email(email):
            raise ValueError("User not found")
        return email

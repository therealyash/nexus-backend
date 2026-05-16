from fastapi import HTTPException, Header
from typing import Optional
import jwt

from app.config import SECRET_KEY, ALGORITHM
from app.database import users_col, BLACKLIST


def verify_token(token: str) -> str:
    if token in BLACKLIST:
        raise HTTPException(status_code=401, detail="Token has been logged out")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or bad Authorization header")
    token = authorization.split(" ")[1]
    email = verify_token(token)
    user = await users_col.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return email

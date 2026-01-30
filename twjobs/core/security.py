from datetime import datetime, timezone

import bcrypt
import jwt

from .config import settings


def hash_password(password: str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )


def verify_password(password: str, hashed_password: str):
    return bcrypt.checkpw(
        password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(sub: int, extra_claims: dict | None = None):
    expires = datetime.now(timezone.utc) + settings.ACCESS_TOKEN_DURATION
    payload = {
        "sub": str(sub),
        "exp": expires,
        **(extra_claims or {}),
    }
    return jwt.encode(
        payload,
        settings.ACCESS_TOKEN_SECRET,
        algorithm=settings.ACCESS_TOKEN_ALGORITHM,
    )

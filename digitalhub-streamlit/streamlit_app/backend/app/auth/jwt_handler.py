from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from jwt import PyJWTError

from app.config import settings


class TokenError(Exception):
    """Raised when a JWT is missing, malformed, or expired."""


def create_access_token(subject: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {"sub": subject, "iat": now, "exp": expire, "type": "access"}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except PyJWTError as exc:
        raise TokenError(str(exc)) from exc

    if payload.get("type") != "access":
        raise TokenError("Invalid token type")
    return payload

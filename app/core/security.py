# app/core/security.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt  # PyJWT
from passlib.context import CryptContext

try:
    # Projede zaten settings varsa onu kullan
    from app.core.config import settings
except Exception:
    # Yedek: env'den oku
    import os
    class _FallbackSettings:
        SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
        ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
        ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    settings = _FallbackSettings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash password for storage."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(
        to_encode,
        getattr(settings, "SECRET_KEY", "dev-secret-change-me"),
        algorithm=getattr(settings, "ALGORITHM", "HS256"),
    )
    return token

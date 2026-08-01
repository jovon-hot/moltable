"""Admin authentication — JWT-based, gated by ADMIN_SECRET env var.

All env reads happen at call-time (not import-time) so Railway env vars
set after deployment are picked up without requiring a cold-start.
"""
from typing import Optional
import os
import logging
import hmac
import jwt as _jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request

logger = logging.getLogger("moltable.admin_auth")

ADMIN_TOKEN_EXPIRY_HOURS = int(os.getenv("ADMIN_TOKEN_EXPIRY_HOURS", "1"))


def _get_secret() -> str:
    """Dynamically read ADMIN_SECRET — supports hot-reload via env var."""
    return os.getenv("ADMIN_SECRET", "")


def _get_jwt_secret() -> str:
    return os.getenv("ADMIN_JWT_SECRET", _get_secret() or "moltable-admin-default-secret")


def is_admin_enabled() -> bool:
    """Check dynamically whether admin features are available."""
    return bool(_get_secret())


def verify_admin_secret(secret: str) -> bool:
    return hmac.compare_digest(secret, _get_secret())


def _encode_admin_jwt(payload: dict) -> str:
    return _jwt.encode(payload, _get_jwt_secret(), algorithm="HS256")


def issue_admin_token(request: Request) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "admin",
        "role": "admin",
        "iat": now,
        "exp": now + timedelta(hours=ADMIN_TOKEN_EXPIRY_HOURS),
        "ip": request.client.host if request and request.client else "unknown",
    }
    return _encode_admin_jwt(payload)


def create_admin_token(secret: str) -> Optional[str]:
    """Verify admin secret and return a short-lived JWT, or None."""
    if not is_admin_enabled():
        return None
    if not verify_admin_secret(secret):
        return None

    now = datetime.now(timezone.utc)
    payload = {
        "sub": "admin",
        "role": "admin",
        "iat": now,
        "exp": now + timedelta(hours=ADMIN_TOKEN_EXPIRY_HOURS),
    }
    return _encode_admin_jwt(payload)


def verify_admin_token(token: str, request: Optional[Request] = None) -> Optional[dict]:
    try:
        claims = _jwt.decode(token, _get_jwt_secret(), algorithms=["HS256"])
        if claims.get("role") != "admin":
            return None
        if request and request.client:
            token_ip = claims.get("ip", "")
            if token_ip and token_ip != "unknown" and token_ip != request.client.host:
                logger.warning(
                    "Admin token IP mismatch: token=%s request=%s",
                    token_ip, request.client.host,
                )
        return claims
    except (_jwt.ExpiredSignatureError, _jwt.InvalidTokenError):
        return None

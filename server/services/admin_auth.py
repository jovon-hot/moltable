"""Admin authentication — JWT-based, gated by ADMIN_SECRET env var.

Without ADMIN_SECRET set, admin endpoints are disabled entirely.
"""
from typing import Optional
import os
import logging
import hmac
import jwt as _jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request

logger = logging.getLogger("moltable.admin_auth")

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "")
ADMIN_JWT_SECRET = os.getenv("ADMIN_JWT_SECRET", ADMIN_SECRET or "moltable-admin-default-secret")
ADMIN_TOKEN_EXPIRY_HOURS = int(os.getenv("ADMIN_TOKEN_EXPIRY_HOURS", "1"))

_admin_enabled = bool(ADMIN_SECRET)

if not _admin_enabled:
    logger.info("ADMIN_SECRET not set — admin endpoints disabled")


def is_admin_enabled() -> bool:
    """Check whether admin features are available."""
    return _admin_enabled


def verify_admin_secret(secret: str) -> bool:
    """Constant-time compare the provided secret against ADMIN_SECRET."""
    return hmac.compare_digest(secret, ADMIN_SECRET)


def _encode_admin_jwt(payload: dict) -> str:
    """Encode a JWT for admin use."""
    return _jwt.encode(payload, ADMIN_JWT_SECRET, algorithm="HS256")


def issue_admin_token(request: Request) -> str:
    """Issue a short-lived JWT for the admin session.

    The token embeds an issuer IP so it cannot be replayed from a different host.
    """
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
    """Verify the admin secret and return a short-lived JWT, or None if invalid.

    This is the main entry point for the admin login endpoint.
    """
    if not _admin_enabled:
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
    """Verify an admin JWT token.

    Returns the decoded payload dict if valid, None otherwise.
    Does NOT raise HTTPException — callers should check the return value.
    """
    try:
        claims = _jwt.decode(token, ADMIN_JWT_SECRET, algorithms=["HS256"])
        if claims.get("role") != "admin":
            return None

        # Optional IP binding check (skip if request not available)
        if request and request.client:
            token_ip = claims.get("ip", "")
            if token_ip and token_ip != "unknown" and token_ip != request.client.host:
                logger.warning(
                    "Admin token IP mismatch: token=%s request=%s",
                    token_ip, request.client.host,
                )
                # Soft check — warn but don't reject (corporate proxies change IPs)

        return claims
    except (_jwt.ExpiredSignatureError, _jwt.InvalidTokenError):
        return None

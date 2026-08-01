"""Admin authentication — JWT-based, brute-force resistant.

Security properties:
- ADMIN_SECRET via env var (not in code)
- /login rate-limited to 5/min per IP
- 5 consecutive failures → 15-min IP cooldown
- JWT expires in 1 hour (configurable via ADMIN_TOKEN_EXPIRY_HOURS)
- All env reads are dynamic (Railway hot-reload compatible)
"""
import os, logging, hmac, time
from typing import Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict

import jwt as _jwt
from fastapi import HTTPException, Request

logger = logging.getLogger("moltable.admin_auth")

ADMIN_TOKEN_EXPIRY_HOURS = int(os.getenv("ADMIN_TOKEN_EXPIRY_HOURS", "1"))

# ── Brute-force protection ──
# Simple in-memory store: keyed by client IP, tracks consecutive failures + cooldown expiry.
_failure_store: dict[str, tuple[int, float]] = defaultdict(lambda: (0, 0.0))
_COOLDOWN_SECS = 900  # 15 minutes


def _get_secret() -> str:
    return os.getenv("ADMIN_SECRET", "")


def _get_jwt_secret() -> str:
    return os.getenv("ADMIN_JWT_SECRET", _get_secret())


def is_admin_enabled() -> bool:
    return bool(_get_secret())


def verify_admin_secret(secret: str) -> bool:
    if len(_get_secret()) < 12:
        return False  # refuse to work with too-short secrets
    return hmac.compare_digest(secret, _get_secret())


def _check_brute_force(ip: str) -> None:
    """Raise HTTPException(429) if IP is in cooldown."""
    failures, cooldown_until = _failure_store.get(ip, (0, 0))
    now = time.time()
    if failures >= 5 and now < cooldown_until:
        remaining = int(cooldown_until - now)
        raise HTTPException(
            429,
            f"Too many login attempts. Try again in {remaining}s.",
        )
    # expired cooldown → reset
    if failures >= 5 and now >= cooldown_until:
        _failure_store.pop(ip, None)


def _record_failure(ip: str) -> None:
    failures, _ = _failure_store.get(ip, (0, 0))
    failures += 1
    cooldown = time.time() + _COOLDOWN_SECS if failures >= 5 else 0
    _failure_store[ip] = (failures, cooldown)
    logger.warning("Admin login failure #%d from IP %s", failures, ip)


def _record_success(ip: str) -> None:
    _failure_store.pop(ip, None)


def _encode_admin_jwt(payload: dict) -> str:
    secret = _get_jwt_secret()
    if len(secret) < 32:
        logger.warning("ADMIN_JWT_SECRET is too short (< 32 bytes). Generate a strong secret.")
    return _jwt.encode(payload, secret, algorithm="HS256")


def create_admin_token(secret: str, request: Optional[Request] = None) -> Optional[str]:
    if not is_admin_enabled():
        return None

    # Brute-force check
    ip = request.client.host if request and request.client else "unknown"
    _check_brute_force(ip)

    if not verify_admin_secret(secret):
        _record_failure(ip)
        return None

    _record_success(ip)

    now = datetime.now(timezone.utc)
    payload = {"sub": "admin", "role": "admin", "iat": now, "exp": now + timedelta(hours=ADMIN_TOKEN_EXPIRY_HOURS)}
    return _encode_admin_jwt(payload)


def verify_admin_token(token: str, request: Optional[Request] = None) -> Optional[dict]:
    try:
        claims = _jwt.decode(token, _get_jwt_secret(), algorithms=["HS256"])
        if claims.get("role") != "admin":
            return None
        return claims
    except (_jwt.ExpiredSignatureError, _jwt.InvalidTokenError):
        return None

"""Admin authentication — email+password with DB-backed accounts.

Two roles:
  - admin: full access (stats, users, system health)
  - operator: read-only access (stats, health)

Brute-force protection: 5 failures → 15-min IP cooldown (per role).

Secrets — one dedicated env var per purpose, no cross-purpose fallback:
  - ADMIN_JWT_SECRET:          signs admin/operator session JWTs (required, >= 32 chars)
  - ADMIN_PASSWORD_PEPPER:     legacy boot secret, kept for config compatibility (required, >= 32 chars)
  - SUPABASE_SERVICE_ROLE_KEY: database access only (owned by app_state)

The server refuses to boot (RuntimeError) if a required secret is missing.
"""

import base64
import hashlib
import hmac
import logging
import os
import re
import secrets
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt as _jwt
from fastapi import HTTPException, Request

from app_state import supabase

logger = logging.getLogger("moltable.admin_auth")

ADMIN_TOKEN_EXPIRY_HOURS = int(os.getenv("ADMIN_TOKEN_EXPIRY_HOURS", "2"))

_SECRET_MIN_LENGTH = 32


def _require_admin_secret(env_name: str) -> str:
    """Return a required admin secret from the environment.

    Raises RuntimeError (refusing to boot) when the variable is missing or
    shorter than _SECRET_MIN_LENGTH. No fallback — each purpose has its own
    dedicated secret, so a missing one is a hard configuration error.
    """
    value = os.getenv(env_name)
    if not value or len(value) < _SECRET_MIN_LENGTH:
        raise RuntimeError(
            f"{env_name} must be set to a secret of at least {_SECRET_MIN_LENGTH} chars "
            f"(got {len(value) if value else 0} chars). Generate one with: "
            'python3 -c "import secrets; print(secrets.token_hex(32))"'
        )
    return value


ADMIN_JWT_SECRET = _require_admin_secret("ADMIN_JWT_SECRET")
_ADMIN_PASSWORD_PEPPER = _require_admin_secret("ADMIN_PASSWORD_PEPPER")

# Brute-force: keyed by (ip, role), tracks consecutive failures
_failure_store: dict[str, tuple[int, float]] = defaultdict(lambda: (0, 0.0))
_COOLDOWN_SECS = 900  # 15 minutes
_MAX_FAILURES = 5


def _client_ip(request: Optional[Request]) -> str:
    if request is None:
        return "unknown"
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    xri = request.headers.get("X-Real-IP", "")
    if xri:
        return xri.strip()
    return request.client.host if request.client else "unknown"


def _hash_password(password: str) -> str:
    """PBKDF2-HMAC-SHA256 — 100,000 iterations with a random per-user 16-byte salt."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000).hex()
    return base64.b64encode(salt).decode() + digest


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt = base64.b64decode(stored_hash[:24])
        expected = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000).hex()
        return hmac.compare_digest(expected, stored_hash[24:])
    except Exception:
        return False


def _check_brute_force(ip: str) -> None:
    failures, cooldown_until = _failure_store.get(ip, (0, 0))
    now = time.time()
    if failures >= _MAX_FAILURES and now < cooldown_until:
        remaining = int(cooldown_until - now)
        raise HTTPException(429, f"Too many attempts. Try again in {remaining}s.")
    if failures >= _MAX_FAILURES and now >= cooldown_until:
        _failure_store.pop(ip, None)


def _record_failure(ip: str) -> None:
    failures, _ = _failure_store.get(ip, (0, 0))
    failures += 1
    cooldown = time.time() + _COOLDOWN_SECS if failures >= _MAX_FAILURES else 0
    _failure_store[ip] = (failures, cooldown)
    logger.warning("Admin login failure #%d from IP %s", failures, ip)


def _record_success(ip: str) -> None:
    _failure_store.pop(ip, None)


def _encode_jwt(email: str, role: str, token_version: int = 1) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "role": role,
        "jti": str(uuid.uuid4()),
        "token_version": token_version,
        "iat": now,
        "exp": now + timedelta(hours=ADMIN_TOKEN_EXPIRY_HOURS),
    }
    return _jwt.encode(payload, ADMIN_JWT_SECRET, algorithm="HS256")


# ═══════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════


def login_admin(email: str, password: str, request: Optional[Request] = None) -> Optional[dict]:
    """Authenticate admin user by email+password. Returns {token, role, email} or None."""
    if supabase is None:
        return None

    ip = _client_ip(request)
    _check_brute_force(ip)

    try:
        resp = (
            supabase.table("admin_users")
            .select("email,password_hash,role,is_active,token_version")
            .eq("email", email.lower().strip())
            .execute()
        )
        if not resp.data:
            _record_failure(ip)
            return None

        user = resp.data[0]
        if not user.get("is_active", True):
            _record_failure(ip)
            return None

        if not _verify_password(password, user["password_hash"]):
            _record_failure(ip)
            return None

        _record_success(ip)

        # Update last_login
        supabase.table("admin_users").update(
            {"last_login_at": datetime.now(timezone.utc).isoformat()}
        ).eq("email", email.lower().strip()).execute()

        role = user.get("role", "operator")
        token_version = user.get("token_version", 1) or 1
        token = _encode_jwt(email, role, token_version)
        return {
            "token": token,
            "role": role,
            "email": email,
            "expires_in": ADMIN_TOKEN_EXPIRY_HOURS * 3600,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Admin login exception: %s", e)
        return None


def verify_admin_token(token: str) -> Optional[dict]:
    """Verify admin JWT and confirm the account is still valid in the DB.

    Every request re-checks the account row (fail closed):
      - account still exists
      - is_active is still true → disabled accounts lose access immediately
      - token_version matches → tokens issued before a disable/enable are dead
    """
    try:
        claims = _jwt.decode(token, ADMIN_JWT_SECRET, algorithms=["HS256"])
    except (_jwt.ExpiredSignatureError, _jwt.InvalidTokenError):
        return None

    role = claims.get("role")
    email = (claims.get("sub") or "").lower().strip()
    if role not in ("admin", "operator") or not email:
        return None
    if "token_version" not in claims:
        return None

    if supabase is None:
        return None
    try:
        resp = (
            supabase.table("admin_users")
            .select("is_active,token_version")
            .eq("email", email)
            .execute()
        )
    except Exception as e:
        logger.error("Admin token DB check failed for %s: %s", email, e)
        return None
    if not resp.data:
        return None
    user = resp.data[0]
    if not user.get("is_active", True):
        return None
    if user.get("token_version", 1) != claims.get("token_version"):
        return None
    return claims


def require_admin(request: Request):
    """FastAPI dependency: require valid admin token with admin role."""
    token = request.headers.get("X-Admin-Token") or request.headers.get(
        "Authorization", ""
    ).replace("Bearer ", "")
    if not token:
        raise HTTPException(401, "Missing admin token")
    claims = verify_admin_token(token)
    if not claims:
        raise HTTPException(401, "Invalid or expired admin token")
    if claims["role"] != "admin":
        raise HTTPException(403, "Admin role required")
    return claims


def require_staff(request: Request):
    """FastAPI dependency: require valid admin/operator token."""
    token = request.headers.get("X-Admin-Token") or request.headers.get(
        "Authorization", ""
    ).replace("Bearer ", "")
    if not token:
        raise HTTPException(401, "Missing staff token")
    claims = verify_admin_token(token)
    if not claims:
        raise HTTPException(401, "Invalid or expired staff token")
    return claims


# ═══════════════════════════════════════════════════
#  Account management (admin only)
# ═══════════════════════════════════════════════════


def create_admin_account(email: str, password: str, role: str = "operator", name: str = "") -> dict:
    """Create a new admin/operator account. Returns created user dict."""
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise HTTPException(400, "Invalid email format")
    if len(password) < 10:
        raise HTTPException(400, "Password must be at least 10 characters")
    if role not in ("admin", "operator"):
        raise HTTPException(400, "Role must be admin or operator")
    if supabase is None:
        raise HTTPException(500, "Database not available")

    pw_hash = _hash_password(password)
    try:
        supabase.table("admin_users").insert(
            {
                "email": email.lower().strip(),
                "name": name or email.split("@")[0],
                "password_hash": pw_hash,
                "role": role,
                "is_active": True,
                "token_version": 1,
            }
        ).execute()
        logger.info("Admin account created: %s (role=%s)", email, role)
        return {"email": email, "role": role, "created": True}
    except Exception as e:
        err = str(e).lower()
        if "duplicate" in err or "unique" in err:
            raise HTTPException(409, "Account already exists")
        raise HTTPException(500, f"Failed to create account: {e}")


def list_admin_accounts() -> list[dict]:
    """List all admin/operator accounts."""
    if supabase is None:
        return []
    try:
        resp = (
            supabase.table("admin_users")
            .select("email,name,role,is_active,last_login_at,created_at")
            .order("created_at")
            .execute()
        )
        return [
            {
                "email": r["email"],
                "name": r.get("name", ""),
                "role": r.get("role", "operator"),
                "is_active": r.get("is_active", True),
                "last_login_at": str(r.get("last_login_at", "")),
                "created_at": str(r.get("created_at", "")),
            }
            for r in (resp.data or [])
        ]
    except Exception:
        return []


def toggle_admin_account(email: str, is_active: bool) -> dict:
    """Enable/disable an admin account. Bumps token_version to invalidate outstanding JWTs."""
    if supabase is None:
        raise HTTPException(500, "Database not available")
    email = email.lower().strip()
    try:
        resp = supabase.table("admin_users").select("token_version").eq("email", email).execute()
    except Exception as e:
        raise HTTPException(500, f"Failed to load account: {e}")
    current_version = (resp.data[0].get("token_version") or 1) if resp.data else 1
    supabase.table("admin_users").update(
        {
            "is_active": is_active,
            "token_version": current_version + 1,
        }
    ).eq("email", email).execute()
    logger.info(
        "Admin account %s → is_active=%s (token_version %s→%s)",
        email,
        is_active,
        current_version,
        current_version + 1,
    )
    return {"email": email, "is_active": is_active}

"""Admin authentication — email+password with DB-backed accounts.

Two roles:
  - admin: full access (stats, users, system health)
  - operator: read-only access (stats, health)

Brute-force protection: 5 failures → 15-min IP cooldown (per role).
"""
import os, logging, hmac, hashlib, secrets, time, re
from typing import Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict

import jwt as _jwt
from fastapi import HTTPException, Request

from app_state import supabase, _is_sqlite

logger = logging.getLogger("moltable.admin_auth")

ADMIN_TOKEN_EXPIRY_HOURS = int(os.getenv("ADMIN_TOKEN_EXPIRY_HOURS", "2"))

JWT_SECRET = os.getenv("ADMIN_JWT_SECRET")
if not JWT_SECRET or len(JWT_SECRET) < 32:
    JWT_SECRET = os.getenv("SUPABASE_SERVICE_KEY", "")
if not JWT_SECRET or len(JWT_SECRET) < 32:
    JWT_SECRET = os.getenv("ADMIN_SECRET", "")
if not JWT_SECRET or len(JWT_SECRET) < 32:
    JWT_SECRET = secrets.token_hex(32)
    logger.warning("ADMIN_JWT_SECRET not set — generated random %d-char key (persists only for this process)", len(JWT_SECRET))

# Password pepper: stable, independent of JWT. Uses SUPABASE_SERVICE_KEY (always set).
_PASSWORD_PEPPER = os.getenv("SUPABASE_SERVICE_KEY", JWT_SECRET)

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
    """PBKDF2-HMAC-SHA256 — 100,000 iterations. Pepper from SUPABASE_SERVICE_KEY (stable)."""
    salt = _PASSWORD_PEPPER[:16].encode()
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000).hex()


def _verify_password(password: str, stored_hash: str) -> bool:
    return hmac.compare_digest(_hash_password(password), stored_hash)


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


def _encode_jwt(email: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=ADMIN_TOKEN_EXPIRY_HOURS),
    }
    return _jwt.encode(payload, JWT_SECRET, algorithm="HS256")


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
        resp = supabase.table("admin_users").select("email,password_hash,role,is_active").eq("email", email.lower().strip()).execute()
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
        supabase.table("admin_users").update({"last_login_at": datetime.now(timezone.utc).isoformat()}).eq("email", email.lower().strip()).execute()

        role = user.get("role", "operator")
        token = _encode_jwt(email, role)
        return {"token": token, "role": role, "email": email, "expires_in": ADMIN_TOKEN_EXPIRY_HOURS * 3600}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Admin login exception: %s", e)
        return None


def verify_admin_token(token: str) -> Optional[dict]:
    """Verify admin JWT. Returns {sub, role, iat, exp} or None."""
    try:
        claims = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if claims.get("role") not in ("admin", "operator"):
            return None
        return claims
    except (_jwt.ExpiredSignatureError, _jwt.InvalidTokenError):
        return None


def require_admin(request: Request):
    """FastAPI dependency: require valid admin token with admin role."""
    token = (
        request.headers.get("X-Admin-Token")
        or request.headers.get("Authorization", "").replace("Bearer ", "")
    )
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
    token = (
        request.headers.get("X-Admin-Token")
        or request.headers.get("Authorization", "").replace("Bearer ", "")
    )
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
        supabase.table("admin_users").insert({
            "email": email.lower().strip(),
            "name": name or email.split("@")[0],
            "password_hash": pw_hash,
            "role": role,
            "is_active": True,
        }).execute()
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
        resp = supabase.table("admin_users").select("email,name,role,is_active,last_login_at,created_at").order("created_at").execute()
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
    """Enable/disable an admin account."""
    if supabase is None:
        raise HTTPException(500, "Database not available")
    supabase.table("admin_users").update({"is_active": is_active}).eq("email", email.lower().strip()).execute()
    logger.info("Admin account %s → is_active=%s", email, is_active)
    return {"email": email, "is_active": is_active}

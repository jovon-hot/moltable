"""Admin API — email+password auth, role-based access.

Roles:
  - admin:   full access (stats, users, account management, health)
  - operator: read-only (stats, health)

Secrets (see services/admin_auth.py): ADMIN_JWT_SECRET + ADMIN_PASSWORD_PEPPER
are required — the server refuses to boot without them. Accounts are stored in
the admin_users table.
"""

import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

import app_state
from services.admin_auth import (
    create_admin_account,
    list_admin_accounts,
    login_admin,
    require_admin,
    require_staff,
    toggle_admin_account,
)

logger = logging.getLogger("moltable.admin")
router = APIRouter(prefix="/api/admin", tags=["admin"])


# ═══════════════════════════════════════════════════
#  Request models
# ═══════════════════════════════════════════════════


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=1, max_length=128)


class CreateAccountRequest(BaseModel):
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=10, max_length=128)
    role: str = Field(default="operator", pattern="^(admin|operator)$")
    name: str = Field(default="", max_length=200)


# ═══════════════════════════════════════════════════
#  Auth endpoints
# ═══════════════════════════════════════════════════


@router.post("/login")
@app_state.limiter.limit("10/minute")
async def admin_login(request: Request, body: LoginRequest):
    """Login with email + password. Returns JWT token + role."""
    result = login_admin(body.email, body.password, request)
    if not result:
        raise HTTPException(401, "Invalid email or password")
    return result


# ═══════════════════════════════════════════════════
#  Stats (admin + operator)
# ═══════════════════════════════════════════════════


@router.get("/stats")
@app_state.limiter.limit("30/minute")
def admin_stats(request: Request, _staff=Depends(require_staff)):
    if app_state.supabase is None or app_state._is_sqlite:
        return {"error": "Stats unavailable in SQLite mode"}

    stats = {
        "total_users": 0,
        "new_users_today": 0,
        "new_users_week": 0,
        "active_users_today": 0,
        "trial_activated": 0,
        "trial_active": 0,
        "total_memories": 0,
        "total_projects": 0,
        "total_personas": 0,
        "api_calls_today": 0,
    }

    import datetime

    today = datetime.date.today().isoformat()

    try:
        r = app_state.supabase.table("users").select("count", count="exact").execute()
        stats["total_users"] = r.count if hasattr(r, "count") else 0
        r = (
            app_state.supabase.table("users")
            .select("count", count="exact")
            .gte("created_at", today)
            .execute()
        )
        stats["new_users_today"] = r.count if hasattr(r, "count") else 0
        r = (
            app_state.supabase.table("users")
            .select("count", count="exact")
            .eq("plan", "pro")
            .execute()
        )
        stats["trial_active"] = r.count if hasattr(r, "count") else 0
        r = (
            app_state.supabase.table("memories")
            .select("count", count="exact")
            .eq("is_archived", False)
            .execute()
        )
        stats["total_memories"] = r.count if hasattr(r, "count") else 0
        r = app_state.supabase.table("projects").select("count", count="exact").execute()
        stats["total_projects"] = r.count if hasattr(r, "count") else 0
        r = app_state.supabase.table("personas").select("count", count="exact").execute()
        stats["total_personas"] = r.count if hasattr(r, "count") else 0
        try:
            r = (
                app_state.supabase.table("users")
                .select("count", count="exact")
                .gte("last_active_at", today)
                .execute()
            )
            stats["active_users_today"] = r.count if hasattr(r, "count") else 0
        except Exception:
            stats["active_users_today"] = 0
    except Exception as e:
        logger.warning("Stats query partial failure: %s", e)

    return {
        "users": {
            "total": stats["total_users"],
            "new_today": stats["new_users_today"],
            "new_week": stats["new_users_week"],
            "active_today": stats["active_users_today"],
            "trial_activated": stats["trial_activated"],
            "trial_active": stats["trial_active"],
        },
        "data": {
            "total_memories": stats["total_memories"],
            "total_projects": stats["total_projects"],
            "total_personas": stats["total_personas"],
        },
        "api": {
            "calls_today": stats["api_calls_today"],
            "error_count": app_state.get_error_count(),
        },
    }


# ═══════════════════════════════════════════════════
#  Users (admin + operator)
# ═══════════════════════════════════════════════════


@router.get("/users")
@app_state.limiter.limit("30/minute")
def admin_users(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    search: str = "",
    _staff=Depends(require_staff),
):
    if app_state.supabase is None or app_state._is_sqlite:
        return {"users": [], "total": 0}

    try:
        q = app_state.supabase.table("users").select(
            "id,email,name,plan,language,created_at", count="exact"
        )
        if search:
            q = q.ilike("email", "%{}%".format(search))
        q = q.order("created_at", desc=True).range(offset, offset + limit - 1)
        resp = q.execute()

        return {
            "users": [
                {
                    "id": r.get("id"),
                    "email": r.get("email"),
                    "name": r.get("name"),
                    "plan": r.get("plan", "free"),
                    "language": r.get("language"),
                    "created_at": str(r.get("created_at", "")),
                }
                for r in (resp.data or [])
            ],
            "total": resp.count if hasattr(resp, "count") else 0,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error("Admin user list failed: %s", e)
        raise HTTPException(500, "Query failed")


# ═══════════════════════════════════════════════════
#  Health (admin + operator)
# ═══════════════════════════════════════════════════


@router.get("/health")
@app_state.limiter.limit("30/minute")
def admin_health(request: Request, _staff=Depends(require_staff)):
    return {
        "status": "ok",
        "db": app_state.supabase is not None,
        "error_count": app_state.get_error_count(),
        "alerts_configured": bool(os.getenv("ALERT_WEBHOOK_URL")),
    }


# ═══════════════════════════════════════════════════
#  Account management (admin only)
# ═══════════════════════════════════════════════════


@router.post("/accounts")
@app_state.limiter.limit("10/minute")
def create_account(request: Request, body: CreateAccountRequest, _admin=Depends(require_admin)):
    """Create a new admin/operator account (admin only)."""
    return create_admin_account(body.email, body.password, body.role, body.name)


@router.get("/accounts")
@app_state.limiter.limit("30/minute")
def list_accounts(request: Request, _admin=Depends(require_admin)):
    """List all admin/operator accounts (admin only)."""
    return {"accounts": list_admin_accounts()}


class ToggleRequest(BaseModel):
    email: str
    is_active: bool


@router.patch("/accounts/toggle")
@app_state.limiter.limit("20/minute")
def toggle_account(request: Request, body: ToggleRequest, _admin=Depends(require_admin)):
    """Enable/disable an admin account (admin only)."""
    return toggle_admin_account(body.email, body.is_active)

# ── 定价查看(Stripe 为唯一价格源)─────────────
@router.get("/pricing")
def admin_pricing(request: Request, _staff=Depends(require_staff)):
    """查看当前 Stripe 定价(USD 分)。价格在 Stripe Dashboard 配置。"""
    from routes.billing import get_pricing, PRICE_IDS
    pricing = get_pricing()
    return {
        "currency": "usd",
        "pricing": pricing,
        "price_ids": {f"{p}_{q}": pid for (p, q), pid in PRICE_IDS.items()},
    }


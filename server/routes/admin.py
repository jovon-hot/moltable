"""Admin API — users, stats, system health.  Gated by ADMIN_SECRET env var."""
import logging
import json
from fastapi import APIRouter, Request, HTTPException, Depends
from app_state import limiter, supabase, _is_sqlite, get_error_count
from services.admin_auth import verify_admin_token, is_admin_enabled

logger = logging.getLogger("moltable.admin")
router = APIRouter(prefix="/api/admin", tags=["admin"])


def _require_admin(request: Request):
    if not is_admin_enabled():
        raise HTTPException(404, "Admin API not enabled — set ADMIN_SECRET env var")
    token = (
        request.headers.get("X-Admin-Token")
        or request.headers.get("Authorization", "").replace("Bearer ", "")
    )
    if not token:
        raise HTTPException(401, "Missing admin token")
    payload = verify_admin_token(token)
    if not payload:
        raise HTTPException(401, "Invalid or expired admin token")
    return payload


@router.post("/login")
@limiter.limit("10/minute")
async def admin_login(request: Request):
    from services.admin_auth import create_admin_token
    body = await request.json()
    secret = body.get("secret", "")
    token = create_admin_token(secret)
    if not token:
        raise HTTPException(401, "Invalid admin secret")
    return {"token": token, "expires_in": 3600}


@router.get("/stats")
@limiter.limit("30/minute")
def admin_stats(request: Request, _admin=Depends(_require_admin)):
    if supabase is None or _is_sqlite:
        return {"error": "Stats unavailable in SQLite mode", "mode": "sqlite"}

    stats = {"total_users": 0, "new_users_today": 0, "new_users_week": 0,
             "active_users_today": 0, "trial_activated": 0, "trial_active": 0,
             "total_memories": 0, "total_projects": 0, "total_personas": 0,
             "api_calls_today": 0}

    import datetime
    today = datetime.date.today().isoformat()

    try:
        r = supabase.table("users").select("count", count="exact").execute()
        stats["total_users"] = r.count if hasattr(r, "count") else 0
        r = supabase.table("users").select("count", count="exact").gte("created_at", today).execute()
        stats["new_users_today"] = r.count if hasattr(r, "count") else 0
        r = supabase.table("users").select("count", count="exact").eq("plan", "pro").execute()
        stats["trial_active"] = r.count if hasattr(r, "count") else 0
        r = supabase.table("memories").select("count", count="exact").eq("is_archived", False).execute()
        stats["total_memories"] = r.count if hasattr(r, "count") else 0
        r = supabase.table("projects").select("count", count="exact").execute()
        stats["total_projects"] = r.count if hasattr(r, "count") else 0
        r = supabase.table("personas").select("count", count="exact").execute()
        stats["total_personas"] = r.count if hasattr(r, "count") else 0
        # active today: users with last_active_at > today
        r = supabase.table("users").select("count", count="exact").gte("last_active_at", today).execute()
        stats["active_users_today"] = r.count if hasattr(r, "count") else 0
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
        "api": {"calls_today": stats["api_calls_today"], "error_count": get_error_count()},
    }


@router.get("/users")
@limiter.limit("30/minute")
def admin_users(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    search: str = "",
    _admin=Depends(_require_admin),
):
    if supabase is None or _is_sqlite:
        return {"users": [], "total": 0}

    try:
        q = supabase.table("users").select(
            "id,email,name,plan,language,created_at,last_active_at", count="exact"
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
                    "last_active_at": str(r.get("last_active_at", "")),
                }
                for r in (resp.data or [])
            ],
            "total": resp.count if hasattr(resp, "count") else 0,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error("Admin user list failed: %s", e)
        raise HTTPException(500, "Query failed: {}".format(str(e)))


@router.get("/health")
@limiter.limit("30/minute")
def admin_health(request: Request, _admin=Depends(_require_admin)):
    import os
    return {
        "status": "ok",
        "db": supabase is not None,
        "error_count": get_error_count(),
        "alerts_configured": bool(os.getenv("ALERT_WEBHOOK_URL")),
        "admin_enabled": is_admin_enabled(),
    }

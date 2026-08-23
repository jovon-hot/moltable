"""Session routes — anonymous session tokens for zero-registration Agent access"""

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app_state import _is_sqlite, get_store, limiter, supabase
from routes.auth import hash_session_token

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

SESSION_TOKEN_PREFIX = "mol_"
SESSION_DURATION_DAYS = 7


# ── Pydantic models ──────────────────────────────────────
class CreateSessionResponse(BaseModel):
    token: str
    expires_at: str
    message: str


class MigrateRequest(BaseModel):
    session_token: str = Field(..., min_length=len(SESSION_TOKEN_PREFIX) + 1)
    api_key: str = Field(..., min_length=1)


class MigrateResponse(BaseModel):
    migrated: bool
    count: int
    session_token: str
    message: str


# ── GET /api/sessions — info ──────────────────────────────
@router.get("")
@limiter.limit("30/minute")
async def list_sessions_info(request: Request):
    """Info about anonymous sessions. Use POST to create one."""
    return {
        "description": "Anonymous sessions allow Agents to use Moltable without registration.",
        "create": "POST /api/sessions  →  returns mol_xxx token (valid 7 days)",
        "migrate": "POST /api/sessions/migrate  →  merge session memories into user account",
    }


# ── POST /api/sessions — create anonymous session ────────
@router.post("")
@limiter.limit("20/hour")
async def create_session(request: Request):
    """Create anonymous session — returns temporary token mol_xxx (7 days).
    Rate limited to 5/hour per IP. Max 100 active sessions globally.
    Expired sessions are cleaned up automatically before creation.
    """
    if supabase is None:
        raise HTTPException(503, "Database not available")

    # ── Clean up expired sessions ──────────────────────────
    try:
        supabase.table("sessions").delete().lt(
            "expires_at", datetime.now(timezone.utc).isoformat()
        ).execute()
    except Exception:
        pass

    # ── Check active session count ────────────────────────
    try:
        active_count = supabase.table("sessions").select("id", count="exact").execute()
        if active_count.count is not None and active_count.count > 1000:
            raise HTTPException(429, "Too many active sessions — try again later")
    except HTTPException:
        raise
    except Exception:
        pass

    token = SESSION_TOKEN_PREFIX + secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_DURATION_DAYS)

    row = {
        "token": hash_session_token(token),
        "expires_at": expires_at.isoformat(),
    }
    # SQLite needs explicit id + session_uuid; Supabase generates them via gen_random_uuid()
    if _is_sqlite:
        import uuid as _uuid

        row["id"] = _uuid.uuid4().hex[:8]
        row["session_uuid"] = str(_uuid.uuid4())

    supabase.table("sessions").insert(row).execute()

    return CreateSessionResponse(
        token=token,
        expires_at=expires_at.isoformat(),
        message="⚠️ Save this token — it won't be shown again. Valid for 7 days.",
    )


# ── POST /api/sessions/migrate — merge session into account ─
@router.post("/migrate")
@limiter.limit("10/hour")
async def migrate_session(request: Request, body: MigrateRequest):
    """Migrate all session memories to an authenticated user account."""
    if supabase is None:
        raise HTTPException(503, "Database not available")

    # 1. Validate session token
    session_token = body.session_token
    if not session_token.startswith(SESSION_TOKEN_PREFIX):
        raise HTTPException(400, "Invalid session token format")

    sess_resp = (
        supabase.table("sessions")
        .select("*")
        .eq("token", hash_session_token(session_token))
        .execute()
    )
    if not sess_resp.data:
        raise HTTPException(404, "Session not found")

    session = sess_resp.data[0]

    if session.get("migrated_at"):
        raise HTTPException(400, "Session already migrated")

    expires_at = session.get("expires_at")
    if expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(400, "Session expired")

    # 2. Validate API key and get user_id
    from routes.auth import hash_api_key

    key_hash = hash_api_key(body.api_key)
    key_resp = supabase.table("api_keys").select("user_id").eq("key_hash", key_hash).execute()
    if not key_resp.data:
        raise HTTPException(401, "Invalid API key")

    user_id = key_resp.data[0]["user_id"]
    # 匿名会话的记忆挂在 session_uuid 下（与 get_user 的 X-Session-Token 分支身份推导一致），
    # 而不是 "session:{token}"，否则 migrate 永远匹配不到任何行
    session_user_id = session.get("user_id") or str(session.get("session_uuid", session_token))

    # 3. Migrate memories using the repository's migrate_user method
    store = get_store()
    count = store.migrate_user(session_user_id, user_id)

    # 4. Mark session as migrated
    supabase.table("sessions").update(
        {
            "user_id": user_id,
            "migrated_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("token", hash_session_token(session_token)).execute()

    return MigrateResponse(
        migrated=True,
        count=count,
        session_token=session_token,
        message=f"Migrated {count} memories to your account.",
    )

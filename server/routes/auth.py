#!/usr/bin/env python3
"""Auth routes — Supabase JWT verification + API key management"""
import hashlib
import logging
import secrets
import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel, Field
from app_state import supabase, limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ── Failed auth audit logging ──────────────────────────
def _log_failed_auth(reason: str, ip_address: str = None, extra: dict = None):
    """Write a failed authentication attempt to audit_logs table."""
    if supabase is None:
        return
    try:
        supabase.table("audit_logs").insert({
            "user_id": None,
            "action": "auth_failed",
            "ip_address": ip_address or "unknown",
            "details": {"reason": reason},
        }).execute()
    except Exception:
        pass  # Never let audit logging itself fail


# ── Pydantic models for input validation ──────────────────
class CreateAPIKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="API key name")


# ── Helpers ──────────────────────────────────────────────
def hash_api_key(key: str) -> str:
    """SHA-256 with pepper salt (PBKDF2-HMAC)."""
    import hashlib
    pepper = os.getenv("API_KEY_PEPPER", "moltable-local-dev-pepper")
    return hashlib.pbkdf2_hmac("sha256", key.encode(), pepper.encode(), 100_000).hex()


# ── JWT user extraction ─────────────────────────────────
async def get_user(request: Request,
                   authorization: str = Header(None),
                   x_api_key: str = Header(None),
                   x_session_token: str = Header(None)) -> str:
    """Extract user_id from Supabase JWT (Bearer token) or API Key (X-API-Key header).
    Also accepts X-Session-Token for anonymous session access (returns session:{token}).
    Failed authentications are logged to audit_logs with IP address.
    """
    ip_address = request.client.host if request and request.client else None
    if authorization:
        token = authorization.removeprefix("Bearer ")
        try:
            resp = supabase.auth.get_user(token)
            return resp.user.id
        except Exception:
            _log_failed_auth("Invalid JWT token", ip_address)
            raise HTTPException(401, "Invalid token")

    if x_api_key:
        key_hash = hash_api_key(x_api_key)
        try:
            resp = supabase.table("api_keys").select("user_id, is_active").eq("key_hash", key_hash).execute()
            if not resp.data:
                _log_failed_auth("Invalid API key", ip_address)
                raise HTTPException(401, "Invalid API key")
            key_record = resp.data[0]
            if not key_record.get("is_active", False):
                _log_failed_auth("Revoked API key", ip_address)
                raise HTTPException(401, "API key revoked")
            return key_record["user_id"]
        except HTTPException:
            raise
        except Exception:
            _log_failed_auth("API key lookup error", ip_address)
            raise HTTPException(401, "Invalid API key")

    if x_session_token:
        # Anonymous session: validate token exists and not expired
        try:
            resp = supabase.table("sessions").select("session_uuid, token, expires_at, migrated_at").eq("token", x_session_token).execute()
            if not resp.data:
                _log_failed_auth("Invalid session token", ip_address)
                raise HTTPException(401, "Invalid session token")
            session = resp.data[0]
            if session.get("migrated_at"):
                _log_failed_auth("Session already migrated", ip_address)
                raise HTTPException(401, "Session already migrated — use API key instead")
            expires_at = session.get("expires_at")
            if expires_at:
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if expires_at < datetime.now(timezone.utc):
                    _log_failed_auth("Session expired", ip_address)
                    raise HTTPException(401, "Session expired — create a new one")
            return str(session.get("session_uuid", x_session_token))
        except HTTPException:
            raise
        except Exception:
            _log_failed_auth("Session token lookup error", ip_address)
            raise HTTPException(401, "Invalid session token")

    _log_failed_auth("Missing authentication headers", ip_address)
    raise HTTPException(401, "Missing Authorization header, X-API-Key header, or X-Session-Token header")


# ── API Key management ─────────────────────────────────
@router.post("/api-keys")
@limiter.limit("20/hour")
def create_api_key(request: Request, body: CreateAPIKeyRequest,
                   user_id: str = Depends(get_user)):
    raw_key = "molt_" + secrets.token_urlsafe(24)
    key_hash = hash_api_key(raw_key)
    prefix = raw_key[:12]  # store prefix for display
    supabase.table("api_keys").insert({
        "user_id": user_id,
        "name": body.name,
        "key_hash": key_hash,
        "key_prefix": prefix,
        "is_active": True,
    }).execute()
    return {
        "key": raw_key,
        "name": body.name,
        "note": "⚠️ Save this — it won't be shown again",
    }


@router.get("/api-keys")
@limiter.limit("60/minute")
def list_api_keys(request: Request, user_id: str = Depends(get_user)):
    return (
        supabase.table("api_keys")
        .select("id,name,key_prefix,is_active,created_at,last_used_at")
        .eq("user_id", user_id)
        .execute()
        .data
    )


@router.delete("/api-keys/{key_id}")
@limiter.limit("30/minute")
def revoke_api_key(request: Request, key_id: str, user_id: str = Depends(get_user)):
    supabase.table("api_keys").update({"is_active": False}).eq("id", key_id).eq("user_id", user_id).execute()
    return {"revoked": True}


# ── Me ─────────────────────────────────────────────────
@router.get("/me")
@limiter.limit("60/minute")
def get_me(request: Request, user_id: str = Depends(get_user)):
    """Return current user info + plan + usage stats."""
    from services.quota import get_usage, PLAN_NAMES, PLAN_LIMITS
    try:
        resp = supabase.table("users").select("id,email,name,timezone,language,plan,created_at").eq("id", user_id).execute()
        if resp.data:
            user = dict(resp.data[0])
            user["usage"] = get_usage(user_id)
            return user
    except Exception:
        pass
    # Fallback
    plan = "free"
    usage = get_usage(user_id)
    return {
        "id": user_id,
        "plan": plan,
        "plan_name": PLAN_NAMES.get(plan, plan),
        "usage": usage,
    }


# ── Agent DID+VC 认证 ──────────────────────────────────
# 相比 get_user() 返回纯 user_id 字符串，
# authenticate_agent() 返回 AuthContext（含 did, persona_id, scopes）。

from services.verifier_service import get_verifier, AuthContext


async def authenticate_agent(
    request: Request,
    authorization: str = Header(None),
    x_agent_vp: str = Header(None),
    x_api_key: str = Header(None),
) -> AuthContext:
    """三层认证，专用于 Agent 发起的请求。

    优先级：
      1. Authorization: Bearer <VP_JWT>  → DID+VC 完整认证
      2. X-Agent-VP: <VP_JWT>            → 同上（简化 header）
      3. X-API-Key（向下兼容）             → 旧 API Key，返回降级 AuthContext

    返回 AuthContext 而非纯 user_id，调用方可以访问：
      - ctx.did        Agent 的 DID
      - ctx.user_id    关联的人类用户 ID
      - ctx.persona_id 当前委托的 Persona（可选）
      - ctx.scopes     权限范围列表
    """
    # ── 方式1 & 2: DID+VC 认证 ──
    vp_token = None
    if authorization and authorization.startswith("Bearer "):
        vp_token = authorization.removeprefix("Bearer ").strip()
    elif x_agent_vp:
        vp_token = x_agent_vp.strip()

    if vp_token:
        verifier = get_verifier()
        import jwt as _jwt
        try:
            unverified = _jwt.decode(vp_token, options={"verify_signature": False})
            vp_obj = unverified.get("vp", {})
            challenge = vp_obj.get("challenge")
        except Exception:
            challenge = None
        return verifier.verify_presentation(vp_token, expected_challenge=challenge)

    # ── 方式3: 旧 API Key（向下兼容，标记 deprecated） ──
    if x_api_key:
        user_id = await get_user(
            request, authorization=None, x_api_key=x_api_key, x_session_token=None
        )
        logger.warning(
            "Agent 使用旧 API Key 认证（建议迁移到 DID+VC）: user=%s", user_id
        )
        return AuthContext(
            did=f"deprecated:api-key:{user_id[:8]}",
            user_id=user_id,
            persona_id=None,
            scopes=["*"],
        )

    raise HTTPException(401, "Missing authentication: use Authorization: Bearer <did_vc_vp> or X-API-Key")


# ── 本地注册/登录 (SQLite 模式, 无需 Supabase) ──────────────────

import hashlib
import re
import uuid as _uuid

_API_KEY_PEPPER = os.getenv("API_KEY_PEPPER", "moltable-local-dev-pepper")

# ── XSS 防护 ────────────────────────────────────────
_HTML_TAG_RE = re.compile(r'<[^>]*>')

def _sanitize(text: str) -> str:
    """移除 HTML 标签防止 XSS。"""
    return _HTML_TAG_RE.sub('', text or '')

def _validate_email(email: str) -> bool:
    """基础邮箱格式验证。"""
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email))

def _hash_password(password: str) -> str:
    """使用 scrypt 进行密码哈希（抗 GPU 暴力破解）。"""
    salt = _API_KEY_PEPPER.encode()[:16]
    return hashlib.scrypt(
        password.encode(), salt=salt, n=16384, r=8, p=1, dklen=64
    ).hex()


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(default="", max_length=200)


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
@limiter.limit("10/hour")
def local_register(request: Request, body: RegisterRequest):
    """本地注册 — SQLite 模式，不依赖 Supabase。"""
    # XSS 防护：清理 HTML 标签
    email = _sanitize(body.email).strip().lower()
    name = _sanitize(body.name or body.email.split("@")[0]).strip()[:200]
    
    # 邮箱格式验证
    if not _validate_email(email):
        raise HTTPException(400, "邮箱格式无效")
    
    # 检查 email 是否已存在
    existing = supabase.table("users").select("id").eq("email", email).execute()
    if existing.data:
        raise HTTPException(409, "该邮箱已注册")

    user_id = str(_uuid.uuid4())
    pw_hash = _hash_password(body.password)

    # 创建用户
    supabase.table("users").insert({
        "id": user_id,
        "email": email,
        "name": name,
        "password_hash": pw_hash,
        "plan": "free",
    }).execute()

    # 自动生成 API Key (使用相同的 PBKDF2 哈希)
    raw_key = "molt_" + secrets.token_urlsafe(24)
    key_hash = hash_api_key(raw_key)
    key_id = str(_uuid.uuid4())

    supabase.table("api_keys").insert({
        "id": key_id,
        "user_id": user_id,
        "name": "默认密钥",
        "key_hash": key_hash,
        "key_prefix": raw_key[:12],
        "is_active": True,
    }).execute()

    logging.getLogger("moltable").info("新用户注册: %s (%s)", email, user_id)
    return {
        "user_id": user_id,
        "key": raw_key,
        "email": email,
        "name": name,
        "message": "注册成功！请保存你的 API Key，它不会再次显示。",
    }


@router.post("/login")
@limiter.limit("30/minute")
def local_login(request: Request, body: LoginRequest):
    """本地登录 — 验证密码，返回用户信息。"""
    email = _sanitize(body.email).strip().lower()
    
    result = supabase.table("users").select("id, email, name, password_hash") \
        .eq("email", email).execute()

    if not result.data:
        raise HTTPException(401, "邮箱或密码错误")

    user = result.data[0]
    expected_hash = _hash_password(body.password)

    if user.get("password_hash") != expected_hash:
        raise HTTPException(401, "邮箱或密码错误")

    user_id = user["id"]

    logging.getLogger("moltable").info("用户登录: %s (%s)", email, user_id)
    
    # 返回已有的活跃 API Key（不生成新的，避免每次登录泄露密钥）
    keys_result = supabase.table("api_keys") \
        .select("id, name, key_prefix") \
        .eq("user_id", user_id) \
        .eq("is_active", True) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()
    
    has_existing_key = keys_result.data and len(keys_result.data) > 0
    
    # 创建临时 session token（7 天有效，用于前端登录态）
    from datetime import timedelta
    import uuid as _ses_uuid
    session_id = str(_ses_uuid.uuid4())
    session_token = "mol_" + secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=7)
    
    supabase.table("sessions").insert({
        "id": session_id,
        "session_uuid": session_id,
        "user_id": user_id,
        "token": session_token,
        "created_at": now.isoformat(),
        "expires_at": expires.isoformat(),
    }).execute()
    
    return {
        "user_id": user_id,
        "has_api_key": has_existing_key,
        "session_token": session_token,
        "email": user["email"],
        "name": user.get("name", ""),
    }

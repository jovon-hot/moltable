#!/usr/bin/env python3
"""Auth routes — Supabase JWT verification + API key management"""

import base64
import hashlib
import hmac
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

from altcha import create_challenge, verify_solution
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app_state import client_ip, limiter, supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ── Failed auth audit logging ──────────────────────────
def _log_failed_auth(reason: str, ip_address: str = None, extra: dict = None):
    """Write a failed authentication attempt to audit_logs table."""
    if supabase is None:
        return
    try:
        supabase.table("audit_logs").insert(
            {
                "user_id": None,
                "action": "auth_failed",
                "ip_address": ip_address or "unknown",
                "details": {"reason": reason},
            }
        ).execute()
    except Exception:
        pass  # Never let audit logging itself fail


# ── Pydantic models for input validation ──────────────────
class CreateAPIKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="API key name")


# ── 生产环境判断 + 密钥 fail-closed ──────────────────────
def _is_production() -> bool:
    return os.getenv("RAILWAY_ENVIRONMENT") == "production" or os.getenv("ENV") == "production"


def _secret_or_fail(env_name: str, dev_default: str) -> str:
    """生产环境缺失即拒绝启动；本地/测试用 dev 默认值。"""
    value = os.getenv(env_name)
    if value:
        return value
    if _is_production():
        raise RuntimeError(
            f"{env_name} 未配置。生产环境拒绝启动，请设置该环境变量（本地开发可用默认值）。"
        )
    return dev_default


_API_KEY_PEPPER = _secret_or_fail("API_KEY_PEPPER", "moltable-local-dev-pepper")
_ALTCHA_HMAC_SECRET = _secret_or_fail("ALTCHA_HMAC_SECRET", "moltable-local-dev-altcha-secret")


# ── Helpers ──────────────────────────────────────────────
def hash_api_key(key: str) -> str:
    """SHA-256 with pepper salt (PBKDF2-HMAC)."""
    import hashlib

    return hashlib.pbkdf2_hmac("sha256", key.encode(), _API_KEY_PEPPER.encode(), 100_000).hex()


def hash_session_token(raw: str) -> str:
    """SHA-256 hex digest of a raw session token (mol_...); only the hash is stored."""
    return hashlib.sha256(raw.encode()).hexdigest()


# ── JWT user extraction ─────────────────────────────────
async def get_user(
    request: Request,
    authorization: str = Header(None),
    x_api_key: str = Header(None),
    x_session_token: str = Header(None),
) -> str:
    """Extract user_id from Supabase JWT (Bearer token) or API Key (X-API-Key header).
    Also accepts X-Session-Token for anonymous session access (returns session:{token}).
    Failed authentications are logged to audit_logs with IP address.
    Also updates last_active_at on the user row (best-effort, silently ignored on failure).
    """
    ip_address = client_ip(request)
    user_id = None

    if authorization:
        token = authorization.removeprefix("Bearer ")
        try:
            resp = supabase.auth.get_user(token)
            user_id = resp.user.id
        except Exception:
            _log_failed_auth("Invalid JWT token", ip_address)
            raise HTTPException(401, "Invalid token")

    elif x_api_key:
        # Check if this is a session token (mol_ prefix) or API key (molt_ prefix)
        if x_api_key.startswith("mol_") and not x_api_key.startswith("molt_"):
            # Session token — look up in sessions table
            try:
                resp = (
                    supabase.table("sessions")
                    .select("session_uuid, token, expires_at, migrated_at, user_id")
                    .eq("token", hash_session_token(x_api_key))
                    .execute()
                )
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
                user_id = session.get("user_id") or str(session.get("session_uuid", x_api_key))
            except HTTPException:
                raise
            except Exception:
                _log_failed_auth("Session token lookup error", ip_address)
                raise HTTPException(401, "Invalid session token")
        else:
            # API key — look up in api_keys table
            key_hash = hash_api_key(x_api_key)
            try:
                resp = (
                    supabase.table("api_keys")
                    .select("user_id, is_active")
                    .eq("key_hash", key_hash)
                    .execute()
                )
                if not resp.data:
                    _log_failed_auth("Invalid API key", ip_address)
                    raise HTTPException(401, "Invalid API key")
                key_record = resp.data[0]
                if not key_record.get("is_active", False):
                    _log_failed_auth("Revoked API key", ip_address)
                    raise HTTPException(401, "API key revoked")
                user_id = key_record["user_id"]
            except HTTPException:
                raise
            except Exception:
                _log_failed_auth("API key lookup error", ip_address)
                raise HTTPException(401, "Invalid API key")

    elif x_session_token:
        # Anonymous session: validate token exists and not expired
        try:
            resp = (
                supabase.table("sessions")
                .select("session_uuid, token, expires_at, migrated_at, user_id")
                .eq("token", hash_session_token(x_session_token))
                .execute()
            )
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
            user_id = session.get("user_id") or str(session.get("session_uuid", x_session_token))
        except HTTPException:
            raise
        except Exception:
            _log_failed_auth("Session token lookup error", ip_address)
            raise HTTPException(401, "Invalid session token")

    else:
        _log_failed_auth("Missing authentication headers", ip_address)
        raise HTTPException(
            401, "Missing Authorization header, X-API-Key header, or X-Session-Token header"
        )

    # ── Track user activity (best-effort, silently ignored on failure) ──
    if user_id and supabase is not None:
        try:
            supabase.table("users").update(
                {
                    "last_active_at": datetime.now(timezone.utc).isoformat(),
                }
            ).eq("id", user_id).execute()
        except Exception:
            pass  # non-critical — don't fail the request over activity tracking

    return user_id


# ── API Key management ─────────────────────────────────
@router.post("/api-keys")
@limiter.limit("20/hour")
def create_api_key(request: Request, body: CreateAPIKeyRequest, user_id: str = Depends(get_user)):
    raw_key = "molt_" + secrets.token_urlsafe(24)
    key_hash = hash_api_key(raw_key)
    prefix = raw_key[:12]  # store prefix for display
    supabase.table("api_keys").insert(
        {
            "user_id": user_id,
            "name": body.name,
            "key_hash": key_hash,
            "key_prefix": prefix,
            "is_active": True,
        }
    ).execute()
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
    supabase.table("api_keys").update({"is_active": False}).eq("id", key_id).eq(
        "user_id", user_id
    ).execute()
    return {"revoked": True}


# ── Me ─────────────────────────────────────────────────
@router.get("/me")
@limiter.limit("60/minute")
def get_me(request: Request, user_id: str = Depends(get_user)):
    """Return current user info + plan + usage stats."""
    from services.quota import PLAN_NAMES, get_usage

    try:
        resp = (
            supabase.table("users")
            .select("id,email,name,timezone,language,plan,created_at,email_verified")
            .eq("id", user_id)
            .execute()
        )
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

from services.verifier_service import AuthContext, get_verifier


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
        logger.warning("Agent 使用旧 API Key 认证（建议迁移到 DID+VC）: user=%s", user_id)
        return AuthContext(
            did=f"deprecated:api-key:{user_id[:8]}",
            user_id=user_id,
            persona_id=None,
            scopes=["*"],
        )

    raise HTTPException(
        401, "Missing authentication: use Authorization: Bearer <did_vc_vp> or X-API-Key"
    )


# ── 本地注册/登录 (SQLite 模式, 无需 Supabase) ──────────────────

import re
import uuid as _uuid

# ── XSS 防护 ────────────────────────────────────────
_HTML_TAG_RE = re.compile(r"<[^>]*>")


def _sanitize(text: str) -> str:
    """移除 HTML 标签防止 XSS。"""
    return _HTML_TAG_RE.sub("", text or "")


def _validate_email(email: str) -> bool:
    """基础邮箱格式验证。"""
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


# 一次性/测试邮箱域名黑名单 —— 防批量注册第一道防线。
# 8月1日 51 个测试账号全是 test.com/t.com/example.com 这类域名。
_DISPOSABLE_EMAIL_DOMAINS = {
    # 明显测试占位
    "test.com", "t.com", "example.com", "example.org", "example.net",
    "test.org", "test.net", "localhost", "localhost.localdomain",
    "test.moltable.ai", "moltable-test.com", "test.moltable.com",
    # 一次性邮箱服务
    "mailinator.com", "10minutemail.com", "guerrillamail.com",
    "temp-mail.org", "tempmail.com", "yopmail.com", "throwawaymail.com",
    "sharklasers.com", "dispostable.com", "maildrop.cc", "getnada.com",
    "trashmail.com", "tempinbox.com", "moakt.com", "mailnesia.com",
}


def _is_disposable_email(email: str) -> bool:
    """判断邮箱域名是否为一次性/测试域名。"""
    domain = email.rsplit("@", 1)[-1].lower() if "@" in email else ""
    return domain in _DISPOSABLE_EMAIL_DOMAINS


def _scrypt_hex(password: str, salt: bytes) -> str:
    """scrypt 派生 64 字节 → hex（兼容 macOS LibreSSL）。"""
    try:
        return hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=64).hex()
    except AttributeError:
        # macOS LibreSSL fallback
        kdf = Scrypt(salt=salt, length=64, n=16384, r=8, p=1)
        return kdf.derive(password.encode()).hex()


def _hash_password(password: str) -> str:
    """scrypt 密码哈希，随机 per-user 盐。格式：base64(16-byte salt) + hex(64-byte digest)。"""
    salt = secrets.token_bytes(16)
    return base64.b64encode(salt).decode() + _scrypt_hex(password, salt)


def _verify_password(password: str, stored_hash: str) -> bool:
    """验证密码。兼容新随机盐格式与 legacy 静态盐格式（已注册用户）。"""
    if not stored_hash:
        return False
    # 新格式：24-char base64 salt + 128-hex digest = 152 chars
    if len(stored_hash) == 152:
        try:
            salt = base64.b64decode(stored_hash[:24])
            return hmac.compare_digest(_scrypt_hex(password, salt), stored_hash[24:])
        except Exception:
            return False
    # legacy 格式：128-hex（静态 PEPPER 盐）
    legacy = _scrypt_hex(password, _API_KEY_PEPPER.encode()[:16])
    return hmac.compare_digest(legacy, stored_hash)


# ── 邮件发送频率限制（防邮件轰炸）──────────────────
EMAIL_COOLDOWN_MINUTES = 5        # 同一邮箱 5 分钟内只发一封
EMAIL_IP_MAX_PER_10MIN = 3        # 同一 IP 10 分钟内最多发 3 封


def _client_ip(request) -> str:
    """提取真实客户端 IP。

    Railway 等反向代理会把真实 IP 放在 X-Forwarded-For，而 request.client.host
    是代理内部 IP（100.64.x.x）且每次请求都变化，直接用它会导致 IP 限流失效。
    """
    if request is not None and getattr(request, "headers", None):
        xff = request.headers.get("x-forwarded-for", "")
        if xff:
            return xff.split(",")[0].strip()
    return request.client.host if request and request.client else "unknown"


def _check_email_rate_limit(email: str, ip: str) -> None:
    """发验证邮件前的频率检查（DB 级：按邮箱冷却 + 按 IP 频率，换 IP 也绕不过按邮箱冷却）。"""
    now = datetime.now(timezone.utc)
    # 按邮箱冷却：5 分钟内该邮箱已发过
    recent = (
        supabase.table("email_send_audit")
        .select("id")
        .eq("email", email)
        .gte("sent_at", (now - timedelta(minutes=EMAIL_COOLDOWN_MINUTES)).isoformat())
        .execute()
    )
    if recent.data:
        raise HTTPException(429, "验证邮件已发送，请查收（含垃圾邮件）。如未收到请稍后再试。")
    # 按 IP 频率：10 分钟内该 IP 发了 ≥ 上限
    ip_recent = (
        supabase.table("email_send_audit")
        .select("id")
        .eq("ip_address", ip)
        .gte("sent_at", (now - timedelta(minutes=10)).isoformat())
        .execute()
    )
    if len(ip_recent.data) >= EMAIL_IP_MAX_PER_10MIN:
        raise HTTPException(429, "发送过于频繁，请稍后再试。")


def _record_email_send(email: str, ip: str) -> None:
    """记录一次验证邮件发送（审计 + 限流依据）。"""
    try:
        supabase.table("email_send_audit").insert(
            {
                "id": str(_uuid.uuid4()),
                "email": email,
                "ip_address": ip,
                "sent_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()
    except Exception:
        pass  # 审计记录失败不阻断主流程


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(default="", max_length=200)
    altcha: str = Field(default="", max_length=8192, description="Altcha PoW base64 payload")


class LoginRequest(BaseModel):
    email: str
    password: str


class ResendVerificationRequest(BaseModel):
    email: str = Field(..., max_length=254)


@router.get("/challenge")
@limiter.limit("60/minute")
def get_altcha_challenge(request: Request):
    """返回 Altcha PoW challenge（人机验证），前端 widget 解算后随注册表单提交。"""
    challenge = create_challenge(
        algorithm="PBKDF2/SHA-256",
        cost=5_000,
        hmac_secret=_ALTCHA_HMAC_SECRET,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    return challenge.to_dict()


@router.post("/register")
@limiter.limit("10/hour")
def local_register(request: Request, body: RegisterRequest):
    """本地注册 — SQLite 模式，不依赖 Supabase。"""
    # 人机验证：Altcha PoW（防机器人批量注册）
    if not body.altcha:
        raise HTTPException(400, "请完成人机验证")
    try:
        vresult = verify_solution(body.altcha, _ALTCHA_HMAC_SECRET)
    except Exception:
        raise HTTPException(400, "验证码无效，请刷新重试")
    if not vresult.verified:
        raise HTTPException(400, "验证码验证失败，请重试")
    if vresult.expired:
        raise HTTPException(400, "验证码已过期，请刷新页面重试")

    # XSS 防护：清理 HTML 标签
    email = _sanitize(body.email).strip().lower()
    name = _sanitize(body.name or body.email.split("@")[0]).strip()[:200]

    # 邮箱格式验证
    if not _validate_email(email):
        raise HTTPException(400, "邮箱格式无效")

    # 防批量注册：拒绝一次性/测试邮箱域名
    if _is_disposable_email(email):
        raise HTTPException(400, "请使用真实邮箱注册")

    # 检查 email 是否已存在
    existing = supabase.table("users").select("id").eq("email", email).execute()
    if existing.data:
        raise HTTPException(409, "该邮箱已注册")

    # 邮件发送频率检查（防轰炸）——提前到创建用户前，避免 429 时已占用邮箱
    ip = _client_ip(request)
    _check_email_rate_limit(email, ip)

    user_id = str(_uuid.uuid4())
    pw_hash = _hash_password(body.password)
    verify_token = secrets.token_urlsafe(32)
    verify_token_expires = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()

    # 创建用户 — email UNIQUE 约束在并发场景提供原子性保证
    try:
        supabase.table("users").insert(
            {
                "id": user_id,
                "email": email,
                "name": name,
                "password_hash": pw_hash,
                "plan": "free",
                "email_verified": False,
                "email_verify_token": verify_token,
                "email_verify_token_expires": verify_token_expires,
            }
        ).execute()
    except Exception as e:
        err_msg = str(e).lower()
        if "duplicate" in err_msg or "unique" in err_msg or "already exists" in err_msg:
            raise HTTPException(409, "该邮箱已注册")
        raise

    # 注意：注册时不发放 API Key。用户验证邮箱后，首次登录时才生成并返回 key。
    logging.getLogger("moltable").info("新用户注册: %s (%s)", email, user_id)

    # 发送邮箱验证邮件（如果配置了 Resend API Key）
    try:
        from email_utils import send_verification_email

        send_verification_email(email, verify_token)
        _record_email_send(email, ip)
    except Exception:
        pass

    return {
        "user_id": user_id,
        "email": email,
        "name": name,
        "email_verified": False,
        "message": "注册成功！我们已发送验证邮件，请点击邮件中的链接确认邮箱。验证后登录即可获取 API Key。",
    }


def _verify_page(success: bool, title: str, sub: str) -> str:
    color = "#22c55e" if success else "#ef4444"
    icon = "✅" if success else "❌"
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{title}</title></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#08090a;color:#f7f8f8;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;">
<div style="max-width:420px;background:#0f1011;border-radius:12px;padding:40px 32px;box-shadow:0 0 0 1px rgba(255,255,255,0.06);text-align:center;">
  <div style="font-size:48px;margin-bottom:16px;">{icon}</div>
  <h1 style="font-size:20px;font-weight:600;margin:0 0 8px;">{title}</h1>
  <p style="font-size:14px;line-height:1.7;color:#8a8f98;margin:0 0 24px;">{sub}</p>
  <a href="https://moltable.ai/login" style="display:inline-block;background:#7170ff;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-size:14px;font-weight:510;">前往登录 →</a>
</div>
</body>
</html>"""


@router.get("/verify-email")
@limiter.limit("30/minute")
def verify_email(request: Request, token: str = ""):
    """验证邮箱 — 用户点击验证邮件中的链接后调用，返回 HTML 结果页。"""
    if not token:
        return HTMLResponse(_verify_page(False, "验证失败", "缺少验证 token。"), status_code=400)

    try:
        result = (
            supabase.table("users")
            .select("id, email_verified, email_verify_token_expires")
            .eq("email_verify_token", token)
            .execute()
        )
    except Exception:
        return HTMLResponse(_verify_page(False, "验证失败", "服务暂时不可用，请稍后重试。"), status_code=500)

    if not result.data:
        return HTMLResponse(_verify_page(False, "验证链接无效", "链接已失效或已被使用，请重新注册或请求新的验证邮件。"), status_code=400)

    user = result.data[0]
    if user.get("email_verified"):
        return HTMLResponse(_verify_page(True, "邮箱已验证", "你的邮箱已验证过，可以直接登录使用了。"))

    # 检查验证链接是否过期（30 分钟有效期）
    _exp = _parse_expiry(user.get("email_verify_token_expires"))
    if _exp and _exp < datetime.now(timezone.utc):
        return HTMLResponse(
            _verify_page(False, "验证链接已过期", "链接已过期（有效期 30 分钟），请重新请求验证邮件。"),
            status_code=400,
        )

    try:
        supabase.table("users").update(
            {"email_verified": True, "email_verify_token": None, "email_verify_token_expires": None}
        ).eq("id", user["id"]).execute()
    except Exception:
        return HTMLResponse(_verify_page(False, "验证失败", "服务暂时不可用，请稍后重试。"), status_code=500)

    logging.getLogger("moltable").info("邮箱验证成功: user=%s", user["id"])
    return HTMLResponse(_verify_page(True, "验证成功！", "你的邮箱已验证，现在可以登录 Moltable 开始备份你的 Agent 灵魂。"))


@router.post("/resend-verification")
@limiter.limit("3/hour")
def resend_verification(request: Request, body: ResendVerificationRequest):
    """重新发送验证邮件 — 带频率限制，防刷邮件。"""
    email = _sanitize(body.email).strip().lower()

    result = (
        supabase.table("users")
        .select("id, email_verified, email_verify_token_expires")
        .eq("email", email)
        .execute()
    )
    if not result.data:
        # 不泄露邮箱是否已注册（防枚举）
        return {"message": "如果该邮箱已注册且未验证，验证邮件已重新发送，请查收。"}

    user = result.data[0]
    if user.get("email_verified"):
        return {"message": "该邮箱已验证，无需重新发送。"}

    # 频率限制（DB 级：按邮箱冷却 + 按 IP 频率，覆盖 register 与 resend 的发送记录）
    ip = _client_ip(request)
    _check_email_rate_limit(email, ip)

    new_token = secrets.token_urlsafe(32)
    new_expires = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
    supabase.table("users").update(
        {"email_verify_token": new_token, "email_verify_token_expires": new_expires}
    ).eq("id", user["id"]).execute()

    try:
        from email_utils import send_verification_email

        send_verification_email(email, new_token)
        _record_email_send(email, ip)
    except Exception:
        pass

    logging.getLogger("moltable").info("重发验证邮件: %s (%s)", email, user["id"])
    return {"message": "验证邮件已重新发送，请查收（30 分钟内有效）。"}


@router.post("/login")
@limiter.limit("5/minute")
def local_login(request: Request, body: LoginRequest):
    """本地登录 — 验证密码，返回用户信息。"""
    email = _sanitize(body.email).strip().lower()

    result = (
        supabase.table("users")
        .select("id, email, name, password_hash, email_verified")
        .eq("email", email)
        .execute()
    )

    if not result.data:
        raise HTTPException(401, "邮箱或密码错误")

    user = result.data[0]
    if not _verify_password(body.password, user.get("password_hash") or ""):
        raise HTTPException(401, "邮箱或密码错误")

    # 邮箱未验证 → 拦截登录（方案 A：验证邮箱后才发放 key / 使用账号）
    if not user.get("email_verified"):
        raise HTTPException(403, "请先验证邮箱，再登录使用")

    user_id = user["id"]

    logging.getLogger("moltable").info("用户登录: %s (%s)", email, user_id)

    # 返回已有的活跃 API Key（不生成新的，避免每次登录泄露密钥）
    keys_result = (
        supabase.table("api_keys")
        .select("id, name, key_prefix")
        .eq("user_id", user_id)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    has_existing_key = keys_result.data and len(keys_result.data) > 0

    # 首次登录（邮箱已验证但还没有 key）→ 生成并返回 API Key
    raw_key = None
    if not has_existing_key:
        raw_key = "molt_" + secrets.token_urlsafe(24)
        supabase.table("api_keys").insert(
            {
                "id": str(_uuid.uuid4()),
                "user_id": user_id,
                "name": "默认密钥",
                "key_hash": hash_api_key(raw_key),
                "key_prefix": raw_key[:12],
                "is_active": True,
            }
        ).execute()
        has_existing_key = True

    # 创建临时 session token（7 天有效，用于前端登录态）
    import uuid as _ses_uuid
    from datetime import timedelta

    session_id = str(_ses_uuid.uuid4())
    session_token = "mol_" + secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=7)

    supabase.table("sessions").insert(
        {
            "id": session_id,
            "session_uuid": session_id,
            "user_id": user_id,
            "token": hash_session_token(session_token),
            "created_at": now.isoformat(),
            "expires_at": expires.isoformat(),
        }
    ).execute()

    return {
        "user_id": user_id,
        "has_api_key": has_existing_key,
        "api_key": raw_key,
        "session_token": session_token,
        "email": user["email"],
        "name": user.get("name", ""),
    }


# ── 同步码 (molt_sync_xxx) — Agent 身份找回 ──────────────────
# Sprint 1 方案：同步码为一次性邀请函，消费后返回账号级 API Key + 用户信息。
# 存储安全：code_hash 用 hash_api_key()（PBKDF2-HMAC-SHA256），明文不落库。


class SyncCodeRequest(BaseModel):
    sync_code: str = Field(
        ..., min_length=1, max_length=256, description="一次性同步码 molt_sync_xxx"
    )


def _hash_sync_code(code: str) -> str:
    """同步码哈希 — 复用 hash_api_key() 的 PBKDF2 算法。"""
    return hash_api_key(code)


def _parse_expiry(value) -> "datetime | None":
    """解析 expires_at（兼容 'Z' 后缀与 datetime 对象）。"""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


@router.get("/sync-code")
@limiter.limit("20/hour")
def generate_sync_code(request: Request, user_id: str = Depends(get_user)):
    """生成新同步码 — 旧码立即作废（pending → revoked）。"""
    from datetime import timedelta

    raw_code = "molt_sync_" + secrets.token_urlsafe(24)
    code_hash = _hash_sync_code(raw_code)
    prefix = raw_code[:12]
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=7)

    # 旧码全部作废
    supabase.table("agent_invites").update(
        {
            "status": "revoked",
            "revoked_at": now.isoformat(),
        }
    ).eq("user_id", user_id).eq("status", "pending").execute()

    supabase.table("agent_invites").insert(
        {
            "id": str(_uuid.uuid4()),
            "user_id": user_id,
            "code_hash": code_hash,
            "code_prefix": prefix,
            "status": "pending",
            "expires_at": expires_at.isoformat(),
            "created_at": now.isoformat(),
        }
    ).execute()

    logging.getLogger("moltable").info("同步码已生成: user=%s prefix=%s", user_id, prefix)
    return {
        "sync_code": raw_code,
        "expires_at": expires_at.isoformat(),
        "note": "一次性使用，7 天有效；生成新码即作废旧码。",
    }


@router.post("/sync")
@limiter.limit("10/minute")
def consume_sync_code(request: Request, body: SyncCodeRequest):
    """同步码消费（无认证 — 新 Agent 首次接入）→ 返回账号级 API Key + 用户信息。

    - 校验 code（pending + 未过期）→ 标记 used（一次性）→ 返回账号级 key。
    - 已使用 / 已作废 / 已过期 → 409（幂等防重放）。
    """
    raw_code = (body.sync_code or "").strip()
    if not raw_code.startswith("molt_sync_"):
        raise HTTPException(400, "同步码格式无效")

    code_hash = _hash_sync_code(raw_code)
    resp = (
        supabase.table("agent_invites")
        .select("id, user_id, status, expires_at")
        .eq("code_hash", code_hash)
        .execute()
    )
    if not resp.data:
        raise HTTPException(404, "同步码无效或不存在")

    invite = resp.data[0]
    now = datetime.now(timezone.utc)
    status = invite.get("status")

    if status == "used":
        raise HTTPException(409, "同步码已使用")
    if status == "revoked":
        raise HTTPException(409, "同步码已作废 — 请重新生成")
    expires_at = _parse_expiry(invite.get("expires_at"))
    if expires_at and expires_at < now:
        raise HTTPException(409, "同步码已过期")

    user_id = invite["user_id"]

    # 一次性：标记 used（条件更新 + 检查影响行数，防并发双花）
    consumed = supabase.table("agent_invites").update(
        {
            "status": "used",
            "used_at": now.isoformat(),
        }
    ).eq("id", invite["id"]).eq("status", "pending").execute()
    if not consumed.data:
        # 并发双花防护：条件 UPDATE 影响 0 行说明已被其他请求消费
        raise HTTPException(409, "同步码已使用")

    # 返回账号级 API Key（明文不落库，仅存哈希 — 与注册一致）
    raw_key = "molt_" + secrets.token_urlsafe(24)
    supabase.table("api_keys").insert(
        {
            "id": str(_uuid.uuid4()),
            "user_id": user_id,
            "name": "同步码恢复",
            "key_hash": hash_api_key(raw_key),
            "key_prefix": raw_key[:12],
            "is_active": True,
        }
    ).execute()

    # 用户信息（best-effort）
    user = {"id": user_id, "name": "", "email": ""}
    try:
        uresp = supabase.table("users").select("id, name, email").eq("id", user_id).execute()
        if uresp.data:
            u = uresp.data[0]
            user = {
                "id": u.get("id") or user_id,
                "name": u.get("name") or "",
                "email": u.get("email") or "",
            }
    except Exception:
        pass

    logging.getLogger("moltable").info("同步码已消费: user=%s", user_id)
    return {
        "api_key": raw_key,
        "user": user,
        "note": "身份已恢复 — 请保存 API Key，它不会再次显示。",
    }


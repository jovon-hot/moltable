"""
Agent 路由 —— DID 注册、VC 签发、Agent 生命周期管理

端点：
  POST /api/agents/enroll          Agent 注册（用 enrollment_token）
  POST /api/agents/renew           Agent 续期（用旧 VC 证明身份）
  POST /api/agents/relocate        Agent 迁移（用 enrollment_token，吊销旧 DID 换新 DID）
  POST /api/enrollment-tokens      生成一次性注册 token（需人类认证）
  GET  /api/agents                 列出用户所有 Agent（需人类认证）

认证方式：
  - 人类用户操作：通过 get_user (Authorization / X-API-Key header)
  - Agent 操作：通过 X-Agent-VP header 提交 Verifiable Presentation
"""

import logging
import secrets
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

from app_state import supabase, limiter
from routes.auth import get_user
from services.issuer_service import get_issuer
from services.verifier_service import get_verifier, AuthContext

logger = logging.getLogger("moltable")

router = APIRouter(prefix="/api", tags=["agents"])


# ── Pydantic 模型 ──────────────────────────────────────────

class EnrollRequest(BaseModel):
    """Agent 注册请求体。"""
    enrollment_token: str = Field(
        ...,
        min_length=1,
        description="一次性注册 token（由 Dashboard 生成）",
    )
    public_key: str = Field(
        ...,
        min_length=1,
        description="Agent 的 Ed25519 公钥（hex 编码，64 字符）",
    )
    platform: str = Field(
        default="hermes",
        max_length=100,
        description="平台标识，如 hermes、claude、chatgpt",
    )
    agent_name: str = Field(
        default="",
        max_length=200,
        description="Agent 名称（可选，用于显示）",
    )


class RenewRequest(BaseModel):
    """Agent 续期请求体。"""
    # 认证由 X-Agent-VP header 承载，请求体可选


class RelocateRequest(BaseModel):
    """Agent 迁移请求体（同 EnrollRequest，用 enrollment_token 验证）。"""
    enrollment_token: str = Field(
        ...,
        min_length=1,
        description="一次性注册 token",
    )
    public_key: str = Field(
        ...,
        min_length=1,
        description="新 Agent 的 Ed25519 公钥（hex 编码）",
    )
    platform: str = Field(
        default="hermes",
        max_length=100,
    )
    agent_name: str = Field(
        default="",
        max_length=200,
    )


class CreateEnrollmentTokenRequest(BaseModel):
    """生成 enrollment token 请求体。"""
    platform: str = Field(
        default="hermes",
        max_length=100,
        description="目标平台",
    )
    agent_name: str = Field(
        default="",
        max_length=200,
        description="Agent 名称",
    )


# ── 响应模型 ───────────────────────────────────────────────

class EnrollResponse(BaseModel):
    """Agent 注册响应。"""
    agent_did: str
    agent_vc: str
    persona_vcs: List[str] = Field(default_factory=list)


class RenewResponse(BaseModel):
    """Agent 续期响应。"""
    agent_vc: str


class RelocateResponse(BaseModel):
    """Agent 迁移响应。"""
    agent_did: str
    agent_vc: str


class EnrollmentTokenResponse(BaseModel):
    """Enrollment token 生成响应。"""
    token: str
    expires_at: str


class AgentInfo(BaseModel):
    """Agent 信息摘要。"""
    did: str
    platform: str
    agent_name: str
    status: str
    last_seen_at: Optional[str] = None
    created_at: Optional[str] = None


# ── Agent 认证依赖 ─────────────────────────────────────────

async def get_agent_auth(
    x_agent_vp: str = Header(None, alias="X-Agent-VP"),
) -> AuthContext:
    """
    从 X-Agent-VP header 提取并验证 Agent 身份。

    用于需要 Agent 认证的端点（renew、relocate 等）。
    验证 VP 签名、内嵌 VC、吊销状态后返回 AuthContext。

    异常：
        HTTPException 401: 缺少 header 或验证失败
    """
    if not x_agent_vp:
        raise HTTPException(
            status_code=401,
            detail="缺少 X-Agent-VP header —— Agent 需提交 Verifiable Presentation",
        )

    verifier = get_verifier()
    try:
        # 不传入 expected_challenge（续期/迁移不需要 challenge）
        auth_ctx = verifier.verify_presentation(x_agent_vp, expected_challenge=None)
        return auth_ctx
    except Exception as exc:
        logger.warning("Agent VP 验证失败: %s", exc)
        raise HTTPException(
            status_code=401,
            detail=f"Agent 认证失败: {exc}",
        )


# ── 帮助函数 ───────────────────────────────────────────────

def _generate_short_id() -> str:
    """生成 8 字符短 ID（uuid4 前 8 位）。"""
    return uuid.uuid4().hex[:8]


def _get_active_personas(user_id: str) -> List[dict]:
    """
    获取用户所有活跃 Persona。

    返回：
        Persona 列表，每项含 id, name, type 等字段
    """
    if supabase is None:
        return []
    try:
        result = (
            supabase.table("personas")
            .select("id, name, type, system_prompt")
            .eq("user_id", user_id)
            .eq("is_active", True)
            .execute()
        )
        return result.data or []
    except Exception as exc:
        logger.error("查询活跃 Persona 失败: %s", exc)
        return []


def _validate_enrollment_token(token: str) -> Optional[dict]:
    """
    验证 enrollment token 的有效性。

    检查：
      - token 存在
      - 未被使用（consumed_at IS NULL）
      - 未过期（expires_at > now）

    返回：
        token 记录字典（含 user_id, platform 等）；无效返回 None
    """
    if supabase is None:
        logger.error("数据库不可用，无法验证 enrollment token")
        return None

    try:
        result = (
            supabase.table("enrollment_tokens")
            .select("token, user_id, platform, agent_name, consumed_at, expires_at")
            .eq("token", token)
            .execute()
        )
        if not result.data:
            logger.warning("Enrollment token 不存在: %s...", token[:16])
            return None

        record = result.data[0]

        # 检查是否已使用
        if record.get("consumed_at") is not None:
            logger.warning("Enrollment token 已被使用: %s...", token[:16])
            return None

        # 检查是否过期
        expires_at = record.get("expires_at")
        if expires_at:
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if expires_at < datetime.now(timezone.utc):
                logger.warning("Enrollment token 已过期: %s...", token[:16])
                return None

        return record
    except Exception as exc:
        logger.error("查询 enrollment token 失败: %s", exc)
        return None


def _consume_enrollment_token(token: str) -> bool:
    """
    标记 enrollment token 为已使用。

    返回：
        True 成功；False 失败
    """
    if supabase is None:
        return False
    try:
        supabase.table("enrollment_tokens").update({
            "consumed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("token", token).execute()
        logger.info("Enrollment token 已标记为使用: %s...", token[:16])
        return True
    except Exception as exc:
        logger.error("标记 enrollment token 失败: %s", exc)
        return False


def _check_did_exists(did: str) -> bool:
    """检查 DID 是否已在注册表中存在。"""
    if supabase is None:
        return False
    try:
        result = (
            supabase.table("did_registry")
            .select("did")
            .eq("did", did)
            .execute()
        )
        return bool(result.data)
    except Exception:
        return False


def _revoke_credentials_for_did(did: str) -> None:
    """
    吊销某个 DID 下的所有活跃凭证。

    在 did_registry 中将 status 设为 revoked，
    在 credentials 表中将相关凭证设为 revoked。
    """
    if supabase is None:
        return
    now = datetime.now(timezone.utc).isoformat()
    try:
        # 吊销 DID 注册
        supabase.table("did_registry").update({
            "status": "revoked",
            "revoked_at": now,
        }).eq("did", did).execute()

        # 吊销相关凭证
        supabase.table("credentials").update({
            "revoked_at": now,
        }).eq("subject_did", did).is_("revoked_at", "null").execute()

        logger.info("已吊销 DID 及其凭证: %s", did)
    except Exception as exc:
        logger.error("吊销 DID %s 失败: %s", did, exc)


def _store_credential(
    credential_jwt: str,
    issuer_did: str,
    subject_did: str,
    credential_type: str,
    claims: dict,
    expires_at: Optional[datetime] = None,
) -> Optional[str]:
    """
    将签发的 VC 存入 credentials 表。

    返回：
        凭证记录 ID；失败返回 None
    """
    if supabase is None:
        return None
    try:
        result = (
            supabase.table("credentials")
            .insert({
                "credential_jwt": credential_jwt,
                "issuer_did": issuer_did,
                "subject_did": subject_did,
                "credential_type": credential_type,
                "claims": claims,
                "expires_at": expires_at.isoformat() if expires_at else None,
            })
            .execute()
        )
        cred_id = result.data[0]["id"] if result.data else None
        logger.debug("凭证已入库: id=%s, type=%s, subject=%s", cred_id, credential_type, subject_did)
        return cred_id
    except Exception as exc:
        logger.error("存储凭证失败: %s", exc)
        return None


# ═══════════════════════════════════════════════════════════
# 端点
# ═══════════════════════════════════════════════════════════

# ── POST /api/agents/enroll ────────────────────────────────

@router.post("/agents/enroll", response_model=EnrollResponse)
@limiter.limit("30/minute")
def agents_enroll(request: Request, body: EnrollRequest):
    """
    Agent 注册 —— 用 Dashboard 生成的 enrollment_token 完成首次注册。

    流程：
      1. 验证 enrollment_token（未被使用、未过期）
      2. 从 token 获取 user_id
      3. 生成 Agent DID（did:web 格式）
      4. 将 DID + 公钥存入 did_registry
      5. 签发 AgentIdentityCredential（90 天有效）
      6. 若用户有活跃 Persona → 自动签发 PersonaDelegationCredential
      7. 标记 enrollment_token 为已使用
      8. 返回 DID + VC(s)

    参数：
        enrollment_token: 一次性连接码
        public_key:       Agent Ed25519 公钥（hex）
        platform:         平台标识
        agent_name:       可选名称
    """
    # ── 步骤 1：验证 enrollment_token ──
    token_record = _validate_enrollment_token(body.enrollment_token)
    if token_record is None:
        raise HTTPException(
            status_code=400,
            detail="Enrollment token 无效、已使用或已过期",
        )
    user_id = token_record["user_id"]

    # 若请求未提供 platform/agent_name，使用 token 中的值
    platform = body.platform or token_record.get("platform", "hermes")
    agent_name = body.agent_name or token_record.get("agent_name", "")

    # ── 步骤 2：验证公钥格式 ──
    # Ed25519 公钥应为 32 字节（64 hex 字符）
    try:
        pub_bytes = bytes.fromhex(body.public_key)
        if len(pub_bytes) != 32:
            raise ValueError(f"公钥长度应为 32 字节，实际为 {len(pub_bytes)} 字节")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"公钥格式无效（需要 hex 编码的 32 字节 Ed25519 公钥）: {exc}",
        )

    # ── 步骤 3：生成 DID ──
    issuer = get_issuer()
    domain = issuer.issuer_did.split(":")[2]  # 从 did:web:<domain>:... 提取域名
    agent_did = issuer.generate_did(domain)

    # 确保 DID 唯一（极小概率重复则重试）
    retries = 0
    while _check_did_exists(agent_did) and retries < 5:
        agent_did = issuer.generate_did(domain)
        retries += 1
    if retries >= 5:
        raise HTTPException(status_code=500, detail="生成唯一 DID 失败，请重试")

    # ── 步骤 4：写入 did_registry ──
    if supabase is not None:
        try:
            supabase.table("did_registry").insert({
                "did": agent_did,
                "user_id": user_id,
                "public_key": body.public_key,
                "key_type": "Ed25519VerificationKey2020",
                "platform": platform,
                "agent_name": agent_name,
                "status": "active",
                "last_seen_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
            logger.info("DID 已注册: %s (user: %s, platform: %s)", agent_did, user_id, platform)
        except Exception as exc:
            logger.error("写入 did_registry 失败: %s", exc)
            raise HTTPException(status_code=500, detail=f"DID 注册失败: {exc}")

    # ── 步骤 5：签发 AgentIdentityCredential ──
    capabilities = ["read_memories", "write_memories", "manage_personas"]
    agent_vc = issuer.issue_agent_identity_credential(
        agent_did=agent_did,
        platform=platform,
        capabilities=capabilities,
        controller_did=agent_did,
    )

    # 将 VC 存入 credentials 表
    _store_credential(
        credential_jwt=agent_vc,
        issuer_did=issuer.issuer_did,
        subject_did=agent_did,
        credential_type=issuer.TYPE_AGENT_IDENTITY,
        claims={"jti": str(uuid.uuid4()), "platform": platform, "capabilities": capabilities},
        expires_at=datetime.now(timezone.utc) + __import__("datetime").timedelta(days=issuer.AGENT_VC_TTL_DAYS),
    )

    # ── 步骤 6：签发 PersonaDelegationCredential ──
    persona_vcs: List[str] = []
    active_personas = _get_active_personas(user_id)
    for persona in active_personas:
        persona_scopes = ["read_memories", "write_memories", "update_persona"]
        pvc = issuer.issue_persona_delegation_credential(
            agent_did=agent_did,
            persona_id=persona["id"],
            scopes=persona_scopes,
        )
        persona_vcs.append(pvc)

        _store_credential(
            credential_jwt=pvc,
            issuer_did=issuer.issuer_did,
            subject_did=agent_did,
            credential_type=issuer.TYPE_PERSONA_DELEGATION,
            claims={"jti": str(uuid.uuid4()), "persona_id": persona["id"], "scopes": persona_scopes},
            expires_at=datetime.now(timezone.utc) + __import__("datetime").timedelta(days=issuer.PERSONA_VC_TTL_DAYS),
        )

    if persona_vcs:
        logger.info("已为 Agent %s 签发 %d 个 Persona 委托凭证", agent_did, len(persona_vcs))

    # ── 步骤 7：标记 enrollment_token 已使用 ──
    _consume_enrollment_token(body.enrollment_token)

    # ── 步骤 8：返回 ──
    return EnrollResponse(
        agent_did=agent_did,
        agent_vc=agent_vc,
        persona_vcs=persona_vcs,
    )


# ── POST /api/agents/renew ─────────────────────────────────

@router.post("/agents/renew", response_model=RenewResponse)
@limiter.limit("30/minute")
def agents_renew(
    request: Request,
    body: RenewRequest,
    agent_auth: AuthContext = Depends(get_agent_auth),
):
    """
    Agent 续期 —— 用旧 VC 证明身份后签发新 VC。

    条件：
      - 旧 AgentIdentityCredential 必须尚未被吊销
      - 旧 VC 过期不超过 30 天则可续期
      - 若 VC 已过期超过 30 天，需要重新 enroll

    认证：
      通过 X-Agent-VP header 提交 VP（含旧 VC）。
      验证通过后，对 VP 中的 Agent DID 签发新的 VC。

    返回：
        新的 agent_vc
    """
    agent_did = agent_auth.did
    user_id = agent_auth.user_id
    old_agent_vc = agent_auth.agent_vc

    # ── 检查旧 VC 是否过期超过 30 天 ──
    import jwt as _jwt
    try:
        unverified = _jwt.decode(old_agent_vc, options={"verify_signature": False})
        exp_timestamp = unverified.get("exp")
        if exp_timestamp:
            exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            grace_period = __import__("datetime").timedelta(days=30)
            if now > exp_time + grace_period:
                raise HTTPException(
                    status_code=410,
                    detail=(
                        f"VC 已过期超过 30 天（过期于 {exp_time.isoformat()}），"
                        f"请重新 enroll"
                    ),
                )
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("解析旧 VC 过期时间失败: %s", exc)
        raise HTTPException(status_code=400, detail=f"无法解析旧 VC: {exc}")

    # ── 从 did_registry 获取 Agent 信息 ──
    if supabase is not None:
        try:
            result = (
                supabase.table("did_registry")
                .select("platform, agent_name")
                .eq("did", agent_did)
                .eq("status", "active")
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=404, detail="Agent DID 未找到或已被吊销")
            platform = result.data[0].get("platform", "hermes")
        except HTTPException:
            raise
        except Exception as exc:
            logger.error("查询 Agent DID 信息失败: %s", exc)
            raise HTTPException(status_code=500, detail=f"查询 Agent 信息失败: {exc}")
    else:
        platform = "hermes"

    # ── 吊销旧 VC ──
    if supabase is not None:
        try:
            # 找到旧 VC 的 jti，吊销它
            old_jti = unverified.get("jti")
            if old_jti:
                supabase.table("credentials").update({
                    "revoked_at": datetime.now(timezone.utc).isoformat(),
                }).eq("subject_did", agent_did).eq("credential_type", "AgentIdentityCredential").is_("revoked_at", "null").execute()
        except Exception as exc:
            logger.warning("吊销旧 VC 失败（非致命）: %s", exc)

    # ── 签发新 VC ──
    issuer = get_issuer()
    capabilities = ["read_memories", "write_memories", "manage_personas"]
    new_agent_vc = issuer.issue_agent_identity_credential(
        agent_did=agent_did,
        platform=platform,
        capabilities=capabilities,
        controller_did=agent_did,
    )

    # 存储新凭证
    _store_credential(
        credential_jwt=new_agent_vc,
        issuer_did=issuer.issuer_did,
        subject_did=agent_did,
        credential_type=issuer.TYPE_AGENT_IDENTITY,
        claims={"jti": str(uuid.uuid4()), "platform": platform, "capabilities": capabilities},
        expires_at=datetime.now(timezone.utc) + __import__("datetime").timedelta(days=issuer.AGENT_VC_TTL_DAYS),
    )

    # 更新 last_seen_at
    if supabase is not None:
        try:
            supabase.table("did_registry").update({
                "last_seen_at": datetime.now(timezone.utc).isoformat(),
            }).eq("did", agent_did).execute()
        except Exception:
            pass

    logger.info("Agent 续期成功: %s", agent_did)
    return RenewResponse(agent_vc=new_agent_vc)


# ── POST /api/agents/relocate ──────────────────────────────

@router.post("/agents/relocate", response_model=RelocateResponse)
@limiter.limit("10/minute")
def agents_relocate(request: Request, body: RelocateRequest):
    """
    Agent 迁移 —— 吊销旧 DID，用 enrollment_token 注册新 DID。

    与 enroll 的区别：
      - relocate 会先吊销该用户已有的活跃 Agent DID
      - 然后再走 enrollment 流程生成新 DID + 新 VC

    参数：
        enrollment_token: 一次性注册 token
        public_key:       新 Agent 的 Ed25519 公钥
        platform:         平台标识
        agent_name:       可选名称
    """
    # ── 验证 enrollment_token ──
    token_record = _validate_enrollment_token(body.enrollment_token)
    if token_record is None:
        raise HTTPException(
            status_code=400,
            detail="Enrollment token 无效、已使用或已过期",
        )
    user_id = token_record["user_id"]

    platform = body.platform or token_record.get("platform", "hermes")
    agent_name = body.agent_name or token_record.get("agent_name", "")

    # ── 验证公钥格式 ──
    try:
        pub_bytes = bytes.fromhex(body.public_key)
        if len(pub_bytes) != 32:
            raise ValueError(f"公钥长度应为 32 字节，实际为 {len(pub_bytes)} 字节")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"公钥格式无效: {exc}",
        )

    # ── 吊销用户所有活跃 Agent DID ──
    if supabase is not None:
        try:
            result = (
                supabase.table("did_registry")
                .select("did")
                .eq("user_id", user_id)
                .eq("status", "active")
                .execute()
            )
            for row in (result.data or []):
                old_did = row["did"]
                _revoke_credentials_for_did(old_did)
                logger.info("已吊销旧 DID: %s (user: %s)", old_did, user_id)
        except Exception as exc:
            logger.error("查询活跃 DID 失败: %s", exc)
            raise HTTPException(status_code=500, detail=f"查询活跃 Agent 失败: {exc}")

    # ── 生成新 DID ──
    issuer = get_issuer()
    domain = issuer.issuer_did.split(":")[2]
    agent_did = issuer.generate_did(domain)

    retries = 0
    while _check_did_exists(agent_did) and retries < 5:
        agent_did = issuer.generate_did(domain)
        retries += 1
    if retries >= 5:
        raise HTTPException(status_code=500, detail="生成唯一 DID 失败，请重试")

    # ── 写入 did_registry ──
    if supabase is not None:
        try:
            supabase.table("did_registry").insert({
                "did": agent_did,
                "user_id": user_id,
                "public_key": body.public_key,
                "key_type": "Ed25519VerificationKey2020",
                "platform": platform,
                "agent_name": agent_name,
                "status": "active",
                "last_seen_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
        except Exception as exc:
            logger.error("写入 did_registry 失败: %s", exc)
            raise HTTPException(status_code=500, detail=f"DID 注册失败: {exc}")

    # ── 签发新 VC ──
    capabilities = ["read_memories", "write_memories", "manage_personas"]
    agent_vc = issuer.issue_agent_identity_credential(
        agent_did=agent_did,
        platform=platform,
        capabilities=capabilities,
        controller_did=agent_did,
    )

    _store_credential(
        credential_jwt=agent_vc,
        issuer_did=issuer.issuer_did,
        subject_did=agent_did,
        credential_type=issuer.TYPE_AGENT_IDENTITY,
        claims={"jti": str(uuid.uuid4()), "platform": platform, "capabilities": capabilities},
        expires_at=datetime.now(timezone.utc) + __import__("datetime").timedelta(days=issuer.AGENT_VC_TTL_DAYS),
    )

    # ── 标记 enrollment_token 已使用 ──
    _consume_enrollment_token(body.enrollment_token)

    logger.info("Agent 迁移完成: %s (user: %s)", agent_did, user_id)
    return RelocateResponse(
        agent_did=agent_did,
        agent_vc=agent_vc,
    )


# ── POST /api/enrollment-tokens ───────────────────────────

@router.post("/enrollment-tokens", response_model=EnrollmentTokenResponse)
@limiter.limit("10/minute")
def create_enrollment_token(
    request: Request,
    body: CreateEnrollmentTokenRequest,
    user_id: str = Depends(get_user),
):
    """
    生成一次性 enrollment token（需人类用户认证）。

    token 格式：molt_enroll_<48 字符随机>
    有效期：5 分钟

    用途：
      Dashboard / CLI 调用此接口生成 token，
      然后在 Agent 端输入 token 完成注册。

    返回：
        token 和过期时间
    """
    # ── 生成 token ──
    random_part = secrets.token_hex(24)  # 24 bytes → 48 hex chars
    token = f"molt_enroll_{random_part}"

    expires_at = datetime.now(timezone.utc) + __import__("datetime").timedelta(minutes=5)

    # ── 存入 enrollment_tokens 表 ──
    if supabase is not None:
        try:
            supabase.table("enrollment_tokens").insert({
                "token": token,
                "user_id": user_id,
                "platform": body.platform,
                "agent_name": body.agent_name,
                "expires_at": expires_at.isoformat(),
            }).execute()
            logger.info(
                "Enrollment token 已生成: %s... (user: %s, platform: %s)",
                token[:24], user_id, body.platform,
            )
        except Exception as exc:
            logger.error("存储 enrollment token 失败: %s", exc)
            raise HTTPException(status_code=500, detail=f"生成 token 失败: {exc}")
    else:
        logger.warning(
            "数据库不可用，enrollment token 仅存在于内存: %s... (user: %s)",
            token[:24], user_id,
        )

    return EnrollmentTokenResponse(
        token=token,
        expires_at=expires_at.isoformat(),
    )


# ── GET /api/agents ────────────────────────────────────────

@router.get("/agents", response_model=List[AgentInfo])
@limiter.limit("120/minute")
def list_agents(
    request: Request,
    user_id: str = Depends(get_user),
):
    """
    列出用户所有 Agent（需人类用户认证）。

    返回 did_registry 中该用户的所有记录（含活跃和已吊销）。
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="数据库不可用")

    try:
        result = (
            supabase.table("did_registry")
            .select("did, platform, agent_name, status, last_seen_at, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        agents = []
        for row in (result.data or []):
            agents.append(AgentInfo(
                did=row.get("did", ""),
                platform=row.get("platform", "unknown"),
                agent_name=row.get("agent_name", ""),
                status=row.get("status", "active"),
                last_seen_at=row.get("last_seen_at"),
                created_at=row.get("created_at"),
            ))
        return agents
    except Exception as exc:
        logger.error("查询 Agent 列表失败: %s", exc)
        raise HTTPException(status_code=500, detail=f"查询 Agent 列表失败: {exc}")

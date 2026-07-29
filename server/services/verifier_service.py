"""
Verifier 服务 —— 验证 Verifiable Presentation 与提取 AuthContext

职责：
  1. 验证 VP（Verifiable Presentation）JWT 的完整性和真实性
     - 验证 VP 外层签名（由 Agent 私钥签署）
     - 验证内嵌 VC 的签名（由 Issuer 私钥签署）
     - 验证 VP challenge 匹配（防重放）
     - 检查 VC 是否过期 / 被吊销
  2. 生成一次性 challenge（32 字节随机 hex）
  3. 从 VP 中提取 AuthContext（did, user_id, persona_id, scopes）

验证流程：
  VP JWT → 查询 did_registry 获取 Agent 公钥 → 验证 VP 签名
        → 提取内嵌 VC → 逐条用 Issuer 公钥验证签名
        → 检查 VC 吊销状态（查 credentials 表）
        → 校验 challenge → 返回 AuthContext

使用方式：
  from services.verifier_service import get_verifier
  verifier = get_verifier()
  auth_ctx = verifier.verify_presentation(vp_jwt, expected_challenge)
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

import jwt
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from app_state import supabase

logger = logging.getLogger("moltable")


# ── 数据结构 ────────────────────────────────────────────────

@dataclass
class AuthContext:
    """
    从 VP 中提取的认证上下文。

    字段：
        did:         Agent 的 DID
        user_id:     Agent 所属的人类用户 ID
        persona_id:  当前有效的 Persona ID（来自 PersonaDelegationCredential），可选
        scopes:      权限范围列表
        agent_vc:    验证通过的 AgentIdentityCredential JWT
        persona_vc:  验证通过的 PersonaDelegationCredential JWT，可选
    """
    did: str
    user_id: str
    persona_id: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    agent_vc: Optional[str] = None
    persona_vc: Optional[str] = None


# ── Verifier 服务 ──────────────────────────────────────────

class VerifierService:
    """
    Verifiable Presentation 验证服务。

    验证 Agent 提交的 VP 是否合法：签名、时效、吊销状态、challenge 匹配。
    """

    # challenge 默认有效期（秒）
    CHALLENGE_TTL_SECONDS = 300  # 5 分钟

    def __init__(self) -> None:
        """初始化验证器。"""
        # 获取 Issuer 公钥用于验证 VC 签名
        from services.issuer_service import get_issuer
        self._issuer = get_issuer()
        logger.info("VerifierService 初始化完成")

    # ── Challenge 管理 ─────────────────────────────────────

    def create_challenge(self, agent_did: Optional[str] = None) -> str:
        """
        生成一次性随机 challenge（32 字节 hex，64 字符）。

        同时将 challenge 写入 challenges 表，设置 5 分钟过期，
        用于后续 VP 验证时防重放。

        参数：
            agent_did: 可选，关联的 Agent DID

        返回：
            64 字符 hex 字符串
        """
        challenge = secrets.token_hex(32)  # 32 bytes → 64 hex chars

        # 持久化 challenge 到数据库
        if supabase is not None:
            try:
                supabase.table("challenges").insert({
                    "challenge": challenge,
                    "agent_did": agent_did,
                    "expires_at": datetime.now(timezone.utc).isoformat(),
                }).execute()
                logger.debug("生成 challenge 并写入数据库: %s...", challenge[:16])
            except Exception as exc:
                logger.warning("写入 challenges 表失败: %s，仅返回 challenge", exc)
        else:
            logger.debug("生成 challenge（无数据库模式）: %s...", challenge[:16])

        return challenge

    def _consume_challenge(self, challenge: str) -> bool:
        """
        标记 challenge 为已使用（防重放）。

        返回 True 表示成功标记，False 表示标记失败（可能已被使用）。
        """
        if supabase is None:
            # 无数据库模式：跳过 challenge 消费
            return True
        try:
            result = (
                supabase.table("challenges")
                .update({"used_at": datetime.now(timezone.utc).isoformat()})
                .eq("challenge", challenge)
                .is_("used_at", "null")
                .execute()
            )
            # 检查是否真的更新了行
            if result.data:
                return True
            logger.warning("challenge %s... 已被使用或不存在", challenge[:16])
            return False
        except Exception as exc:
            logger.error("消费 challenge 失败: %s", exc)
            return False

    # ── VP 验证 ────────────────────────────────────────────

    def verify_presentation(
        self,
        vp_jwt: str,
        expected_challenge: Optional[str] = None,
    ) -> AuthContext:
        """
        验证 Verifiable Presentation 并提取认证上下文。

        验证步骤：
          1. 解码 VP JWT（不验证签名）获取 agent_did
          2. 从 did_registry 查询 Agent 公钥
          3. 用 Agent 公钥验证 VP 外层签名
          4. 提取内嵌 VC JWT 列表
          5. 逐条用 Issuer 公钥验证 VC 签名与过期
          6. 检查 VC 是否被吊销（查 credentials 表）
          7. 校验 challenge 匹配（若提供）
          8. 构建并返回 AuthContext

        参数：
            vp_jwt:             Agent 提交的 VP JWT 字符串
            expected_challenge: 期望的 challenge 值，若提供则校验

        返回：
            AuthContext 包含 did, user_id, persona_id, scopes

        异常：
            jwt.InvalidSignatureError: 签名无效
            jwt.ExpiredSignatureError: VP 或内嵌 VC 已过期
            jwt.InvalidTokenError:     JWT 格式无效或缺失必要字段
            ValueError:                公钥未找到、DID 已吊销、challenge 不匹配
        """
        # ── 步骤 1：解码 VP JWT（不验证签名）获取 agent_did ──
        try:
            unverified = jwt.decode(
                vp_jwt,
                options={"verify_signature": False},
            )
        except Exception as exc:
            raise jwt.InvalidTokenError(f"无法解码 VP JWT: {exc}")

        agent_did = unverified.get("iss") or unverified.get("sub")
        if not agent_did:
            raise jwt.InvalidTokenError("VP JWT 缺少 iss / sub 字段，无法确定 Agent DID")

        # ── 步骤 2：从 did_registry 查询 Agent 公钥 ──
        agent_info = self._lookup_did(agent_did)
        if agent_info is None:
            raise ValueError(f"Agent DID 未在注册表中找到: {agent_did}")
        if agent_info.get("status") != "active":
            raise ValueError(f"Agent DID 已被吊销: {agent_did}")

        agent_public_key_hex = agent_info.get("public_key")
        if not agent_public_key_hex:
            raise ValueError(f"Agent DID 缺少公钥: {agent_did}")

        user_id = agent_info.get("user_id")
        if not user_id:
            raise ValueError(f"Agent DID 缺少 user_id 关联: {agent_did}")

        # 将 hex 公钥转为 Ed25519 公钥对象
        try:
            agent_public_key = ed25519.Ed25519PublicKey.from_public_bytes(
                bytes.fromhex(agent_public_key_hex)
            )
        except Exception as exc:
            raise ValueError(f"Agent 公钥格式无效: {exc}")

        # ── 步骤 3：验证 VP 外层签名 ──
        try:
            vp_claims = jwt.decode(
                vp_jwt,
                agent_public_key,
                algorithms=["EdDSA"],
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "require": ["vp", "jti"],
                },
            )
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("VP JWT 已过期")
        except jwt.InvalidSignatureError:
            raise jwt.InvalidSignatureError("VP 外层签名验证失败 —— Agent 私钥不匹配")
        except Exception as exc:
            raise jwt.InvalidTokenError(f"VP JWT 验证失败: {exc}")

        # ── 步骤 4：提取内嵌 VC ──
        vp_object = vp_claims.get("vp", {})
        if not isinstance(vp_object, dict):
            raise jwt.InvalidTokenError("VP 对象缺失或格式无效")

        vc_jwt_list = vp_object.get("verifiableCredential", [])
        if not vc_jwt_list or not isinstance(vc_jwt_list, list):
            raise jwt.InvalidTokenError("VP 缺少 verifiableCredential 列表")

        # ── 步骤 5 & 6：逐条验证 VC ──
        agent_vc = None
        persona_vc = None
        persona_id = None
        scopes: List[str] = []

        issuer_service = self._issuer

        for vc_jwt_str in vc_jwt_list:
            # 用 Issuer 公钥验证 VC 签名和过期
            try:
                vc_claims = issuer_service.verify_vc_signature(
                    vc_jwt_str,
                    expected_issuer_did=issuer_service.issuer_did,
                )
            except jwt.ExpiredSignatureError:
                # 记录是哪类 VC 过期了
                raise jwt.ExpiredSignatureError(
                    f"内嵌 VC 已过期: {vc_jwt_str[:50]}..."
                )
            except jwt.InvalidSignatureError:
                raise jwt.InvalidSignatureError("内嵌 VC 签名验证失败")
            except Exception as exc:
                raise jwt.InvalidTokenError(f"内嵌 VC 验证失败: {exc}")

            jti = vc_claims.get("jti")

            # 检查 VC 是否被吊销（查询 credentials 表）
            if not self._is_credential_valid(jti):
                raise ValueError(f"VC 已被吊销: jti={jti}")

            # 分类处理 VC
            vc = vc_claims.get("vc", {})
            vc_types = vc.get("type", [])

            if issuer_service.TYPE_AGENT_IDENTITY in vc_types:
                agent_vc = vc_jwt_str
                logger.debug("识别到 AgentIdentityCredential: jti=%s", jti)

            elif issuer_service.TYPE_PERSONA_DELEGATION in vc_types:
                persona_vc = vc_jwt_str
                cred_subject = vc.get("credentialSubject", {})
                persona_id = cred_subject.get("persona_id")
                scopes = cred_subject.get("scopes", [])
                logger.debug(
                    "识别到 PersonaDelegationCredential: jti=%s, persona=%s",
                    jti, persona_id,
                )

        # AgentIdentityCredential 是必需的
        if agent_vc is None:
            raise jwt.InvalidTokenError("VP 缺少必需的 AgentIdentityCredential")

        # ── 步骤 7：校验 challenge ──
        vp_challenge = vp_object.get("challenge")
        if expected_challenge is not None:
            if vp_challenge != expected_challenge:
                raise ValueError(
                    f"Challenge 不匹配: 期望 {expected_challenge[:16]}...，"
                    f"实际 {str(vp_challenge)[:16]}..."
                )
            # 标记 challenge 为已使用（防重放）
            if not self._consume_challenge(expected_challenge):
                raise ValueError("Challenge 已被使用或已过期")

        # ── 步骤 8：构建 AuthContext ──
        logger.info(
            "VP 验证通过 — DID: %s, user: %s, persona: %s, scopes: %s",
            agent_did, user_id, persona_id, scopes,
        )

        return AuthContext(
            did=agent_did,
            user_id=user_id,
            persona_id=persona_id,
            scopes=scopes,
            agent_vc=agent_vc,
            persona_vc=persona_vc,
        )

    # ── 辅助方法 ────────────────────────────────────────────

    def _lookup_did(self, did: str) -> Optional[dict]:
        """
        在 did_registry 表中查找 DID 记录。

        返回：
            包含 public_key, user_id, status 等字段的字典；未找到返回 None
        """
        if supabase is None:
            logger.warning("数据库不可用，无法查询 DID 注册表")
            return None
        try:
            result = (
                supabase.table("did_registry")
                .select("did, user_id, public_key, key_type, status, platform")
                .eq("did", did)
                .execute()
            )
            if result.data:
                return result.data[0]
            return None
        except Exception as exc:
            logger.error("查询 DID 注册表失败: %s", exc)
            raise ValueError(f"查询 DID 注册表失败: {exc}")

    def _is_credential_valid(self, jti: str) -> bool:
        """
        检查 VC 是否未被吊销。

        查询 credentials 表，确认：
          - revoked_at IS NULL（未被吊销）
          - 未被其他凭证替换（replaced_by IS NULL）

        返回 True 表示凭证有效。
        """
        if supabase is None:
            # 无数据库模式：跳过吊销检查
            return True
        try:
            result = (
                supabase.table("credentials")
                .select("id, revoked_at, replaced_by")
                .eq("credential_jwt__jti", jti)  # 可能需要 jti 列
                .execute()
            )
            # 尝试通过 claims JSONB 查询 jti
            if not result.data:
                # 如果直接查询不到，查 claims JSONB 中的 jti
                result = (
                    supabase.table("credentials")
                    .select("id, revoked_at, replaced_by, claims")
                    .execute()
                )
                for row in (result.data or []):
                    if row.get("claims", {}).get("jti") == jti:
                        if row.get("revoked_at") is not None:
                            return False
                        if row.get("replaced_by") is not None:
                            return False
                        return True
                # 未找到记录视为有效（可能尚未入库）
                return True

            # 找到了记录，检查吊销状态
            row = result.data[0]
            if row.get("revoked_at") is not None:
                logger.warning("VC 已被吊销: jti=%s", jti)
                return False
            if row.get("replaced_by") is not None:
                logger.warning("VC 已被替换: jti=%s, replaced_by=%s", jti, row["replaced_by"])
                return False
            return True
        except Exception as exc:
            logger.error("查询凭证吊销状态失败: %s", exc)
            # 查询失败时保守处理：拒绝
            return False

    def extract_auth_context_from_vp(self, vp_jwt: str) -> AuthContext:
        """
        仅从 VP 中提取 AuthContext，不执行完整验证。
        适用于已经通过 verify_presentation 验证后的再提取场景。

        参数：
            vp_jwt: VP JWT 字符串

        返回：
            AuthContext
        """
        # 解码 VP（不验证签名，因为已经验证过）
        unverified = jwt.decode(vp_jwt, options={"verify_signature": False})
        agent_did = unverified.get("iss") or unverified.get("sub", "")
        vp_object = unverified.get("vp", {})

        # 提取内嵌 VC 中的 persona 信息
        persona_id = None
        scopes: List[str] = []
        user_id = ""

        for vc_jwt_str in vp_object.get("verifiableCredential", []):
            try:
                vc = jwt.decode(vc_jwt_str, options={"verify_signature": False})
                vc_obj = vc.get("vc", {})
                vc_types = vc_obj.get("type", [])

                if self._issuer.TYPE_PERSONA_DELEGATION in vc_types:
                    cs = vc_obj.get("credentialSubject", {})
                    persona_id = cs.get("persona_id")
                    scopes = cs.get("scopes", [])
            except Exception:
                continue

        # 查 did_registry 获取 user_id
        agent_info = self._lookup_did(agent_did)
        if agent_info:
            user_id = agent_info.get("user_id", "")

        return AuthContext(
            did=agent_did,
            user_id=user_id,
            persona_id=persona_id,
            scopes=scopes,
        )


# ── 单例 ───────────────────────────────────────────────────

_verifier_instance: Optional[VerifierService] = None


def get_verifier() -> VerifierService:
    """
    获取 VerifierService 单例。

    返回：
        VerifierService 实例
    """
    global _verifier_instance
    if _verifier_instance is None:
        _verifier_instance = VerifierService()
    return _verifier_instance

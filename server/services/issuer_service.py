"""
Issuer 服务 —— 签发 Verifiable Credential (JWT + Ed25519)

职责：
  1. 管理 Issuer 的 Ed25519 密钥对（从环境变量加载或自动生成）
  2. 签发 AgentIdentityCredential：证明 Agent 身份、平台、能力
  3. 签发 PersonaDelegationCredential：将 Persona 权限委托给 Agent
  4. 验证 VC 签名：verify_vc_signature()

VC 格式遵循 W3C Verifiable Credentials Data Model v1.1，
使用 JWT 作为 proof 载体（EdDSA / Ed25519 签名）。

使用方式：
  from services.issuer_service import get_issuer
  issuer = get_issuer()
  vc_jwt = issuer.issue_agent_identity_credential(...)
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional

import jwt
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger("moltable")

# ── Issuer 配置 ─────────────────────────────────────────────
# Issuer DID 的域名部分，从环境变量读取，默认 moltable.io
_MOLTABLE_DOMAIN = os.getenv("MOLTABLE_DOMAIN", "moltable.io")
# Issuer 的完整 DID
ISSUER_DID = os.getenv("MOLTABLE_ISSUER_DID", f"did:web:{_MOLTABLE_DOMAIN}:issuer")
_KEY_FILE = os.getenv("MOLTABLE_ISSUER_KEY_FILE", os.path.join(os.path.dirname(__file__), "..", ".moltable_issuer_key"))


class IssuerService:
    """
    Verifiable Credential 签发服务。

    使用 Ed25519 密钥对 + PyJWT 签发符合 W3C VC 标准的 JWT。
    Issuer 私钥通过环境变量 MOLTABLE_ISSUER_KEY 注入（hex 编码的 32 字节种子）。
    若未设置，首次启动时自动生成并打印到日志。
    """

    # VC 类型常量
    TYPE_AGENT_IDENTITY = "AgentIdentityCredential"
    TYPE_PERSONA_DELEGATION = "PersonaDelegationCredential"

    # 默认过期时间
    AGENT_VC_TTL_DAYS = 90          # Agent 身份凭证 90 天
    PERSONA_VC_TTL_DAYS = 30        # Persona 委托凭证 30 天

    def __init__(self) -> None:
        """初始化 Issuer：加载或生成 Ed25519 密钥对。"""
        self._private_key: ed25519.Ed25519PrivateKey = self._load_or_generate_key()
        self._public_key: ed25519.Ed25519PublicKey = self._private_key.public_key()
        self.issuer_did: str = ISSUER_DID

        # 将公钥以 hex 形式缓存，方便外部使用
        public_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.public_key_hex: str = public_bytes.hex()
        logger.info("IssuerService 初始化完成 — Issuer DID: %s", self.issuer_did)

    # ── 密钥管理 ───────────────────────────────────────────

    def _load_or_generate_key(self) -> ed25519.Ed25519PrivateKey:
        """从环境变量、持久化文件加载 Ed25519 私钥，或自动生成并保存。

        优先级:
          1. 环境变量 MOLTABLE_ISSUER_KEY (hex)
          2. 持久化文件 _KEY_FILE (~/.moltable_issuer_key)
          3. 自动生成 → 保存到 _KEY_FILE → 继续使用
        """
        key_env = os.getenv("MOLTABLE_ISSUER_KEY")
        if key_env:
            try:
                seed = bytes.fromhex(key_env.strip())
                if len(seed) != 32:
                    raise ValueError(f"私钥种子长度应为 32 字节，实际为 {len(seed)} 字节")
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
                logger.info("已从 MOLTABLE_ISSUER_KEY 加载 Issuer Ed25519 私钥")
                return private_key
            except Exception as exc:
                logger.error("解析 MOLTABLE_ISSUER_KEY 失败: %s，尝试从文件加载", exc)

        # 尝试从持久化文件加载
        try:
            if os.path.exists(_KEY_FILE):
                with open(_KEY_FILE, "r") as f:
                    seed_hex = f.read().strip()
                if len(seed_hex) == 64:
                    seed = bytes.fromhex(seed_hex)
                    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
                    logger.info("已从持久化文件加载 Issuer 私钥: %s", _KEY_FILE)
                    return private_key
        except Exception as exc:
            logger.warning("从文件加载 Issuer 私钥失败: %s", exc)

        # 自动生成新密钥 → 持久化到文件
        private_key = ed25519.Ed25519PrivateKey.generate()
        seed = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        seed_hex = seed.hex()
        try:
            with open(_KEY_FILE, "w") as f:
                f.write(seed_hex + "\n")
            os.chmod(_KEY_FILE, 0o600)
            logger.info("已生成并持久化 Issuer 私钥到: %s", _KEY_FILE)
        except Exception as exc:
            logger.warning(
                "⚠️  无法持久化 Issuer 私钥到 %s: %s。密钥仅在内存中。"
                "重启后将丢失，请设置 MOLTABLE_ISSUER_KEY 环境变量。\n"
                "    密钥值为: %s", _KEY_FILE, exc, seed_hex
            )
        return private_key

    # ── VC 签发 ────────────────────────────────────────────

    def issue_agent_identity_credential(
        self,
        agent_did: str,
        platform: str,
        capabilities: List[str],
        controller_did: Optional[str] = None,
        ttl_days: int = AGENT_VC_TTL_DAYS,
    ) -> str:
        """
        签发 AgentIdentityCredential。

        参数：
            agent_did:     Agent 的 DID（subject）
            platform:      平台标识，如 "hermes", "claude", "chatgpt"
            capabilities:  Agent 能力列表，如 ["read_memories", "manage_personas"]
            controller_did: 控制者 DID，默认同 agent_did
            ttl_days:      凭证有效期（天），默认 90

        返回：
            JWT 字符串（紧凑序列化）
        """
        now = datetime.now(timezone.utc)
        jti = str(uuid.uuid4())

        payload = {
            # JWT 标准声明
            "iss": self.issuer_did,                     # 签发者
            "sub": agent_did,                            # 主体
            "iat": now,
            "nbf": now,
            "exp": now + self._days_to_timedelta(ttl_days),
            "jti": jti,
            # VC 核心声明
            "vc": {
                "@context": [
                    "https://www.w3.org/2018/credentials/v1",
                    "https://moltable.io/credentials/v1",
                ],
                "type": [
                    "VerifiableCredential",
                    self.TYPE_AGENT_IDENTITY,
                ],
                "credentialSubject": {
                    "id": agent_did,
                    "platform": platform,
                    "capabilities": capabilities,
                    "controller": controller_did or agent_did,
                },
            },
        }

        token = jwt.encode(payload, self._private_key, algorithm="EdDSA")
        logger.info("签发 AgentIdentityCredential — subject: %s, jti: %s", agent_did, jti)
        return token

    def issue_persona_delegation_credential(
        self,
        agent_did: str,
        persona_id: str,
        scopes: List[str],
        ttl_days: int = PERSONA_VC_TTL_DAYS,
    ) -> str:
        """
        签发 PersonaDelegationCredential —— 将 Persona 操作权限委托给 Agent。

        参数：
            agent_did:   Agent 的 DID（subject）
            persona_id:  被委托的 Persona ID
            scopes:      权限范围，如 ["read_memories", "write_memories", "update_persona"]
            ttl_days:    凭证有效期（天），默认 30

        返回：
            JWT 字符串
        """
        now = datetime.now(timezone.utc)
        jti = str(uuid.uuid4())

        payload = {
            "iss": self.issuer_did,
            "sub": agent_did,
            "iat": now,
            "nbf": now,
            "exp": now + self._days_to_timedelta(ttl_days),
            "jti": jti,
            "vc": {
                "@context": [
                    "https://www.w3.org/2018/credentials/v1",
                    "https://moltable.io/credentials/v1",
                ],
                "type": [
                    "VerifiableCredential",
                    self.TYPE_PERSONA_DELEGATION,
                ],
                "credentialSubject": {
                    "id": agent_did,
                    "persona_id": persona_id,
                    "scopes": scopes,
                },
            },
        }

        token = jwt.encode(payload, self._private_key, algorithm="EdDSA")
        logger.info(
            "签发 PersonaDelegationCredential — subject: %s, persona: %s, jti: %s",
            agent_did, persona_id, jti,
        )
        return token

    # ── VC 签名验证 ────────────────────────────────────────

    def verify_vc_signature(self, vc_jwt: str, expected_issuer_did: Optional[str] = None) -> dict:
        """
        验证 VC JWT 的 Ed25519 签名，并可选校验 issuer DID。

        参数：
            vc_jwt:              JWT 字符串
            expected_issuer_did:  期望的签发者 DID，若提供则校验 iss 字段匹配

        返回：
            解码后的 claims 字典

        异常：
            jwt.InvalidSignatureError: 签名无效
            jwt.ExpiredSignatureError: VC 已过期
            jwt.InvalidTokenError:     JWT 格式无效
            ValueError:                issuer DID 不匹配
        """
        # 使用 Issuer 公钥验证 EdDSA 签名
        claims = jwt.decode(
            vc_jwt,
            self._public_key,
            algorithms=["EdDSA"],
            options={
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
                "require": ["iss", "sub", "jti", "vc"],
            },
        )

        # 校验 issuer DID
        if expected_issuer_did is not None and claims.get("iss") != expected_issuer_did:
            raise ValueError(
                f"Issuer DID 不匹配: 期望 {expected_issuer_did}，实际 {claims.get('iss')}"
            )

        # 校验 VC 结构完整性
        vc = claims.get("vc", {})
        if not isinstance(vc, dict):
            raise jwt.InvalidTokenError("VC 声明缺失或格式无效")
        if "credentialSubject" not in vc:
            raise jwt.InvalidTokenError("VC 缺少 credentialSubject 字段")

        return claims

    # ── 工具方法 ───────────────────────────────────────────

    @staticmethod
    def generate_did(domain: str, short_id: Optional[str] = None) -> str:
        """
        生成 did:web 格式的 DID。

        格式：did:web:<domain>:agent:<uuid8>

        参数：
            domain:    域名部分，如 moltable.io
            short_id:  可选，8 字符标识符；不提供则自动生成 uuid4 前 8 位

        返回：
            DID 字符串
        """
        if short_id is None:
            short_id = uuid.uuid4().hex[:8]
        # did:web 中将域名中的冒号转义，但简单域名不需要
        return f"did:web:{domain}:agent:{short_id}"

    @staticmethod
    def _days_to_timedelta(days: int):
        """将天数转为 timedelta，避免直接导入 datetime.timedelta 的麻烦。"""
        from datetime import timedelta
        return timedelta(days=days)


# ── 单例 ───────────────────────────────────────────────────

_issuer_instance: Optional[IssuerService] = None


def get_issuer() -> IssuerService:
    """
    获取 IssuerService 单例。

    首次调用时初始化 Ed25519 密钥对（从环境变量加载或自动生成）。
    后续调用返回同一个实例。

    返回：
        IssuerService 实例
    """
    global _issuer_instance
    if _issuer_instance is None:
        _issuer_instance = IssuerService()
    return _issuer_instance

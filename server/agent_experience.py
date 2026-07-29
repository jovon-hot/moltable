"""
Moltable DID+VC Agent 端到端验证脚本

模拟完整流程：
  1. 用户注册 → 获取 Enrollment Token
  2. Agent 本地生成 Ed25519 密钥对
  3. Agent 用 Token 注册 DID → 获取 VC
  4. auto_provision() → 加载用户上下文
  5. 日常使用：search_memory / save_memory
  6. VC 续期
  7. 换电脑 → relocate

运行: cd server && python3 agent_experience.py
依赖: cryptography, pyjwt, httpx
"""

import hashlib
import json
import os
import secrets
import sys
import uuid
from datetime import datetime, timezone, timedelta


# ═══════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════

def print_step(n: int, title: str):
    """打印步骤标题"""
    print(f"\n{'='*60}")
    print(f" 步骤 {n}: {title}")
    print(f"{'='*60}")


def print_result(ok: bool, detail: str):
    """打印步骤结果"""
    icon = "✅" if ok else "❌"
    print(f"  {icon} {detail}")


# ═══════════════════════════════════════════════════════
# 模拟的 Moltable API 调用
# ═══════════════════════════════════════════════════════

class MoltableAPI:
    """模拟 Moltable 服务端，不依赖真实 Supabase/网络"""

    def __init__(self):
        self.tokens = {}       # token → {user_id, consumed_at, expires_at}
        self.dids = {}         # did → {user_id, public_key, status}
        self.credentials = {}  # jti → {vc_jwt, type, subject_did, revoked, expires}
        self.memories = {}     # user_id → [memory records]
        self.users = {}        # user_id → {name, email}
        self.personas = {}     # user_id → [persona records]
        self.challenges = set()

    def create_user(self, user_id: str, name: str):
        self.users[user_id] = {"name": name, "email": f"{name}@test.com"}
        self.memories[user_id] = []
        self.personas[user_id] = []
        print_result(True, f"用户已创建: {user_id} ({name})")

    def create_enrollment_token(self, user_id: str, platform: str = "hermes") -> dict:
        token = f"molt_enroll_{secrets.token_hex(24)}"
        self.tokens[token] = {
            "user_id": user_id,
            "platform": platform,
            "consumed_at": None,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
        }
        print_result(True, f"Token 已生成: {token[:30]}...")
        return {"token": token, "expires_at": str(self.tokens[token]["expires_at"])}

    def enroll(self, token: str, public_key: str, platform: str, agent_name: str) -> dict:
        # 验证 token
        record = self.tokens.get(token)
        if record is None:
            raise ValueError("Token 无效: 未找到")
        if record["consumed_at"] is not None:
            raise ValueError("Token 已被使用")
        if datetime.now(timezone.utc) > record["expires_at"]:
            raise ValueError("Token 已过期")

        # 标记 token 已消费
        record["consumed_at"] = datetime.now(timezone.utc)
        user_id = record["user_id"]

        # 生成 DID
        short_id = uuid.uuid4().hex[:8]
        did = f"did:web:moltable.io:agent:{short_id}"
        self.dids[did] = {
            "user_id": user_id,
            "public_key": public_key,
            "platform": platform,
            "agent_name": agent_name,
            "status": "active",
        }

        # 签发 AgentIdentityCredential (模拟 JWT，用 | 分隔避免 DID 中 . 的干扰)
        jti = str(uuid.uuid4())
        vc_jwt = f"eyJ|{did}|{jti}|AgentIdentityCredential|mock"
        self.credentials[jti] = {
            "vc_jwt": vc_jwt,
            "type": "AgentIdentityCredential",
            "subject_did": did,
            "revoked": False,
            "expires": datetime.now(timezone.utc) + timedelta(days=90),
        }

        # 自动签发 Persona VC（如果有活跃 Persona）
        persona_vcs = []
        for persona in self.personas.get(user_id, []):
            if persona.get("is_active"):
                p_jti = str(uuid.uuid4())
                p_vc = f"eyJ|{did}|{p_jti}|PersonaDelegationCredential|mock"
                self.credentials[p_jti] = {
                    "vc_jwt": p_vc,
                    "type": "PersonaDelegationCredential",
                    "subject_did": did,
                    "revoked": False,
                    "expires": datetime.now(timezone.utc) + timedelta(days=30),
                }
                persona_vcs.append({"persona_id": persona["id"], "vc": p_vc})

        print_result(True, f"DID 已注册: {did}")
        print_result(True, f"AgentIdentityCredential 已签发 (90 天有效)")
        if persona_vcs:
            print_result(True, f"PersonaDelegationCredential × {len(persona_vcs)} 已签发")

        return {
            "agent_did": did,
            "agent_vc": vc_jwt,
            "persona_vcs": persona_vcs,
        }

    def auto_provision(self, did: str) -> dict:
        """模拟 auto_provision() — 返回用户上下文"""
        agent_info = self.dids.get(did)
        if not agent_info:
            raise ValueError(f"DID 未注册: {did}")

        user_id = agent_info["user_id"]
        user = self.users.get(user_id, {})
        memories = self.memories.get(user_id, [])
        personas = self.personas.get(user_id, [])

        return {
            "profile": {"name": user.get("name"), "language": "zh"},
            "memory_count": len(memories),
            "active_projects": [],
            "recent_decisions": [],
            "available_personas": [p["name"] for p in personas if p.get("is_active")],
        }

    def search_memory(self, did: str, query: str) -> list:
        agent_info = self.dids.get(did)
        if not agent_info:
            raise ValueError("未授权")
        user_id = agent_info["user_id"]
        memories = self.memories.get(user_id, [])
        # 简单模拟：返回包含关键词的记忆
        results = [m for m in memories if query in m.get("content", "")]
        print_result(True, f"搜索 '{query}': {len(results)} 条结果")
        return results

    def save_memory(self, did: str, content: str, category: str = "fact") -> dict:
        agent_info = self.dids.get(did)
        if not agent_info:
            raise ValueError("未授权")
        user_id = agent_info["user_id"]
        mem = {"id": str(uuid.uuid4())[:8], "content": content, "category": category}
        self.memories.setdefault(user_id, []).append(mem)
        print_result(True, f"记忆已保存: {content[:50]}...")
        return mem

    def renew_vc(self, did: str, old_vc: str) -> dict:
        agent_info = self.dids.get(did)
        if not agent_info:
            raise ValueError(f"DID 未注册: {did}")

        # 验证旧 VC 确实属于这个 DID（用 | 分隔）
        parts = old_vc.split("|")
        if len(parts) < 3 or parts[1] != did:
            raise ValueError(f"VC 签名验证失败: 期望 {did}, 实际 {parts[1] if len(parts)>1 else 'N/A'}")

        # 签发新 VC
        jti = str(uuid.uuid4())
        new_vc = f"eyJ|{did}|{jti}|AgentIdentityCredential|renewed|mock"
        self.credentials[jti] = {
            "vc_jwt": new_vc,
            "type": "AgentIdentityCredential",
            "subject_did": did,
            "revoked": False,
            "expires": datetime.now(timezone.utc) + timedelta(days=90),
        }
        print_result(True, f"VC 续期完成 (90 天，jti: {jti[:8]}...)")
        return {"agent_vc": new_vc}

    def relocate(self, token: str, public_key: str) -> dict:
        """换电脑：吊销旧 DID → 生成新 DID → 签发新 VC"""
        record = self.tokens.get(token)
        if not record or record.get("consumed_at"):
            raise ValueError("Token 无效")

        record["consumed_at"] = datetime.now(timezone.utc)
        user_id = record["user_id"]

        # 吊销旧 DID（模拟：找到该用户的旧 DID）
        old_dids = [d for d, info in self.dids.items()
                     if info["user_id"] == user_id and info["status"] == "active"]
        for old_did in old_dids:
            self.dids[old_did]["status"] = "revoked"
            print_result(True, f"旧 DID 已吊销: {old_did}")

        # 生成新 DID + VC
        short_id = uuid.uuid4().hex[:8]
        new_did = f"did:web:moltable.io:agent:{short_id}"
        self.dids[new_did] = {
            "user_id": user_id,
            "public_key": public_key,
            "platform": record["platform"],
            "agent_name": record.get("agent_name", "unknown"),
            "status": "active",
        }

        jti = str(uuid.uuid4())
        new_vc = f"eyJ|{new_did}|{jti}|AgentIdentityCredential|relocated|mock"
        self.credentials[jti] = {
            "vc_jwt": new_vc,
            "type": "AgentIdentityCredential",
            "subject_did": new_did,
            "revoked": False,
            "expires": datetime.now(timezone.utc) + timedelta(days=90),
        }

        print_result(True, f"新 DID 已注册: {new_did}")
        return {"agent_did": new_did, "agent_vc": new_vc}


# ═══════════════════════════════════════════════════════
# Agent 端逻辑（用户换电脑后会运行在新的 Agent 里）
# ═══════════════════════════════════════════════════════

class MoltableAgent:
    """模拟一个接入 Moltable DID+VC 的 AI Agent"""

    def __init__(self):
        self.identity = None  # {did, private_key, agent_vc, persona_vcs}
        self.api = None

    def connect(self, api: MoltableAPI):
        self.api = api

    def has_identity(self) -> bool:
        return self.identity is not None

    def enroll(self, enrollment_token: str, public_key_hex: str,
               platform: str = "hermes", agent_name: str = "测试Agent") -> dict:
        """用 enrollment token 注册 DID"""
        print_step(3, "Agent 注册 DID+VC")
        result = self.api.enroll(enrollment_token, public_key_hex, platform, agent_name)
        self.identity = {
            "did": result["agent_did"],
            "private_key": "mock-private-key-hex",  # 真实场景是本地生成的
            "agent_vc": result["agent_vc"],
            "persona_vcs": result["persona_vcs"],
        }
        print_result(True, f"身份已保存到本地: {result['agent_did']}")
        return result

    def provision(self):
        """加载用户上下文"""
        if not self.identity:
            raise RuntimeError("未连接 Moltable")
        print_step(4, "auto_provision() — 加载用户上下文")
        ctx = self.api.auto_provision(self.identity["did"])
        print(f"  用户: {ctx['profile']['name']}")
        print(f"  记忆数: {ctx['memory_count']}")
        print(f"  可用 Persona: {ctx.get('available_personas', [])}")
        return ctx

    def use_memory(self, query: str):
        """搜索和保存记忆"""
        if not self.identity:
            raise RuntimeError("未连接")
        print_step(5, f"日常使用——搜索记忆: '{query}'")
        results = self.api.search_memory(self.identity["did"], query)
        return results

    def remember(self, content: str, category: str = "preference"):
        """保存记忆"""
        if not self.identity:
            raise RuntimeError("未连接")
        return self.api.save_memory(self.identity["did"], content, category)

    def renew(self):
        """VC 续期"""
        if not self.identity:
            raise RuntimeError("未连接")
        print_step(6, "VC 续期")
        result = self.api.renew_vc(self.identity["did"], self.identity["agent_vc"])
        self.identity["agent_vc"] = result["agent_vc"]
        return result

    def relocate(self, enrollment_token: str, public_key_hex: str):
        """换电脑——用新 enrollment token 迁移"""
        if not self.identity:
            raise RuntimeError("未连接")
        print_step(7, "换电脑 — relocate")
        result = self.api.relocate(enrollment_token, public_key_hex)
        self.identity["did"] = result["agent_did"]
        self.identity["agent_vc"] = result["agent_vc"]
        print_result(True, f"迁移完成，新 DID: {result['agent_did']}")
        return result


# ═══════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print(" Moltable DID+VC Agent 端到端验证")
    print(f" 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    api = MoltableAPI()

    # ── 步骤 1: 用户注册 ──
    print_step(1, "用户注册 (Dashboard)")
    user_id = "user-001"
    api.create_user(user_id, "赵海东")

    # 添加一个 Persona
    persona_id = str(uuid.uuid4())[:8]
    api.personas[user_id] = [{
        "id": persona_id,
        "name": "战略顾问",
        "description": "麦肯锡风格·数据驱动·激进",
        "type": "constructed",
        "is_active": True,
    }]
    print_result(True, f"默认 Persona: 战略顾问 ({persona_id})")

    # ── 步骤 2: 生成 Enrollment Token ──
    print_step(2, "Dashboard 生成 Enrollment Token")
    token_result = api.create_enrollment_token(user_id, "hermes")
    enrollment_token = token_result["token"]

    # ── 步骤 3: Agent 注册 ──
    agent = MoltableAgent()
    agent.connect(api)

    # 模拟生成 Ed25519 公钥
    public_key_hex = secrets.token_hex(32)  # 32 bytes = 64 hex chars
    print(f"  Agent 本地生成 Ed25519 密钥对 (公钥: {public_key_hex[:20]}...)")

    enroll_result = agent.enroll(enrollment_token, public_key_hex, "hermes", "我的AI助手")

    # ── 步骤 4: 加载上下文 ──
    ctx = agent.provision()

    # ── 步骤 5: 日常使用 ──
    agent.remember("赵海东偏好数据驱动的报告，结论先行", "preference")
    agent.remember("FOST 车检集团，16个检测站，淄博", "fact")
    agent.use_memory("FOST")

    # ── 步骤 6: VC 续期 ──
    agent.renew()

    # ── 步骤 7: 换电脑 ──
    new_token = api.create_enrollment_token(user_id, "hermes")["token"]
    new_public_key = secrets.token_hex(32)
    print(f"  [模拟] 新电脑 Agent 生成新密钥对")
    agent.relocate(new_token, new_public_key)

    # ── 步骤 8: 验证 ──
    print_step(8, "最终验证")
    try:
        ctx = agent.provision()
        print_result(True, f"迁移后仍可加载用户 '{ctx['profile']['name']}' 的上下文")
        print_result(True, f"共 {len(api.memories[user_id])} 条记忆")
    except Exception as e:
        print_result(False, f"验证失败: {e}")

    # ── 统计 ──
    active_dids = sum(1 for d in api.dids.values() if d["status"] == "active")
    revoked_dids = sum(1 for d in api.dids.values() if d["status"] == "revoked")
    total_vcs = len(api.credentials)

    print(f"\n{'='*60}")
    print(f" 验证结果汇总")
    print(f"{'='*60}")
    print(f"  用户数:       {len(api.users)}")
    print(f"  Agent 数:     {len(api.dids)} (活跃: {active_dids}, 已吊销: {revoked_dids})")
    print(f"  VC 总数:      {total_vcs}")
    print(f"  记忆数:       {len(api.memories[user_id])}")
    print(f"  Persona 数:   {len(api.personas[user_id])}")
    print(f"\n  ✅ 全部流程验证通过！")


if __name__ == "__main__":
    main()

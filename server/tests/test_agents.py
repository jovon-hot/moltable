"""
Agent 路由测试 —— DID 注册、VC 签发、Enrollment Token、Agent 列表

测试覆盖：
  POST /api/agents/enroll        — 有效 token 注册 / 已使用 token 拒登
  POST /api/enrollment-tokens    — 生成一次性注册 token
  GET  /api/agents               — 列出用户所有 Agent
"""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient


# ═══════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════

def _make_mock_chain(return_data: list):
    """
    构造一个 Supabase 链式调用的 MagicMock，
    使得任意深度的链（如 .select().eq().execute()）最终返回含有所给 data 的响应。
    """
    final = MagicMock()
    final.data = return_data
    # MagicMock 默认返回自身，因此 .select().eq().limit().order() 等都能自动串联，
    # 只需在最终 .execute() 处设置 return_value
    chain = MagicMock()
    chain.execute.return_value = final
    return chain


def _build_supabase_mock(table_responses: dict):
    """
    构造一个 supabase MagicMock，按表名返回不同的 mock 对象。

    参数：
        table_responses: dict[str, MagicMock]
            表名 → 该表对应的 mock 对象（需自行设置 .execute.return_value.data）

    返回：
        MagicMock —— 模拟 supabase 客户端
    """
    mock_supabase = MagicMock()

    def _table(name: str):
        return table_responses.get(name, MagicMock())

    mock_supabase.table.side_effect = _table
    return mock_supabase


def _build_issuer_mock() -> MagicMock:
    """构造 issuer_service 的 MagicMock，返回可控的 DID 和 VC。"""
    mock_issuer = MagicMock()
    mock_issuer.issuer_did = "did:web:test.moltable.io:issuer"
    mock_issuer.generate_did.return_value = "did:web:test.moltable.io:agent:testabcd"
    mock_issuer.issue_agent_identity_credential.return_value = (
        "eyJhbGciOiJFZERTQSJ9.mock-agent-vc-jwt"
    )
    mock_issuer.issue_persona_delegation_credential.return_value = (
        "eyJhbGciOiJFZERTQSJ9.mock-persona-vc-jwt"
    )
    mock_issuer.TYPE_AGENT_IDENTITY = "AgentIdentityCredential"
    mock_issuer.TYPE_PERSONA_DELEGATION = "PersonaDelegationCredential"
    mock_issuer.AGENT_VC_TTL_DAYS = 90
    mock_issuer.PERSONA_VC_TTL_DAYS = 30
    return mock_issuer


# ═══════════════════════════════════════════════════════════════
# 有效的公钥（32 字节 × 2 → 64 hex 字符的 Ed25519 公钥）
# ═══════════════════════════════════════════════════════════════

VALID_PUBLIC_KEY = (
    "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325aa02100000000001"
    "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325aa02100000000001"
)[:64]  # 保证恰好 64 hex 字符 = 32 字节


# ═══════════════════════════════════════════════════════════════
# 测试 1：有效 enrollment_token → 注册成功
# ═══════════════════════════════════════════════════════════════

def test_enroll_with_valid_token():
    """
    测试 POST /api/agents/enroll 使用有效的 enrollment_token。

    验证：
      - mock supabase 返回未消费的 enrollment_token 记录
      - mock did_registry insert 成功
      - 返回 200，响应体含 agent_did 和 agent_vc
    """
    from main import app
    client = TestClient(app)

    # ── 构造 enrollment_token 记录（未被使用、未过期）──
    token_record = {
        "token": "molt_enroll_validtesttoken1234567890abcdef12345678",
        "user_id": "test-user-id",
        "platform": "test-platform",
        "agent_name": "test-agent",
        "consumed_at": None,
        "expires_at": "2099-12-31T23:59:59+00:00",
    }

    # ── 构造各表的 mock 链 ──
    enroll_select_chain = _make_mock_chain([token_record])
    enroll_select_chain.eq.return_value = enroll_select_chain  # 保持链: .eq() 返回自身
    enroll_update_chain = _make_mock_chain([])
    enroll_update_chain.eq.return_value = enroll_update_chain
    did_insert_chain = _make_mock_chain([{"did": "did:web:test.moltable.io:agent:testabcd"}])
    did_check_chain = _make_mock_chain([])          # _check_did_exists → 不存在
    did_check_chain.eq.return_value = did_check_chain
    personas_chain = _make_mock_chain([])            # _get_active_personas → 空列表
    cred_insert_chain = _make_mock_chain([{"id": "cred-001"}])

    # 按表名分配 mock
    table_mocks = {
        "enrollment_tokens": MagicMock(),
        "did_registry": MagicMock(),
        "personas": MagicMock(),
        "credentials": MagicMock(),
    }
    # enrollment_tokens: .select() 链 和 .update() 链
    table_mocks["enrollment_tokens"].select.return_value = enroll_select_chain
    table_mocks["enrollment_tokens"].update.return_value = enroll_update_chain
    # did_registry: .insert() 和 .select() 链
    table_mocks["did_registry"].insert.return_value = did_insert_chain
    table_mocks["did_registry"].select.return_value = did_check_chain
    # personas: .select() 链
    table_mocks["personas"].select.return_value = personas_chain
    # credentials: .insert() 链
    table_mocks["credentials"].insert.return_value = cred_insert_chain

    mock_supabase = _build_supabase_mock(table_mocks)
    mock_issuer = _build_issuer_mock()

    with patch("routes.agents.get_issuer", return_value=mock_issuer), \
         patch("routes.agents.supabase", mock_supabase):
        resp = client.post("/api/agents/enroll", json={
            "enrollment_token": "molt_enroll_validtesttoken1234567890abcdef12345678",
            "public_key": VALID_PUBLIC_KEY,
            "platform": "test-platform",
            "agent_name": "test-agent",
        })

    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "agent_did" in data
    assert "agent_vc" in data
    assert data["agent_did"] == "did:web:test.moltable.io:agent:testabcd"
    assert data["agent_vc"] == "eyJhbGciOiJFZERTQSJ9.mock-agent-vc-jwt"


# ═══════════════════════════════════════════════════════════════
# 测试 2：已使用的 enrollment_token → 400
# ═══════════════════════════════════════════════════════════════

def test_enroll_expired_token():
    """
    测试 POST /api/agents/enroll 使用已被消费的 enrollment_token。

    验证：
      - mock supabase 返回 consumed_at 不为 null 的记录
      - 返回 400，提示 token 无效或已使用
    """
    from main import app
    client = TestClient(app)

    # ── enrollment_token 记录（已被消费）──
    token_record = {
        "token": "molt_enroll_usedtoken1234567890abcdef123456789",
        "user_id": "test-user-id",
        "platform": "test-platform",
        "agent_name": "test-agent",
        "consumed_at": "2025-01-01T00:00:00+00:00",  # ← 不为 null
        "expires_at": "2099-12-31T23:59:59+00:00",
    }

    enroll_select_chain = _make_mock_chain([token_record])

    table_mocks = {
        "enrollment_tokens": MagicMock(),
    }
    table_mocks["enrollment_tokens"].select.return_value = enroll_select_chain

    mock_supabase = _build_supabase_mock(table_mocks)

    with patch("routes.agents.supabase", mock_supabase):
        resp = client.post("/api/agents/enroll", json={
            "enrollment_token": "molt_enroll_usedtoken1234567890abcdef123456789",
            "public_key": VALID_PUBLIC_KEY,
            "platform": "test-platform",
        })

    assert resp.status_code == 400, f"期望 400，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "detail" in data
    assert "无效" in data["detail"] or "已使用" in data["detail"]


# ═══════════════════════════════════════════════════════════════
# 测试 3：生成 enrollment token
# ═══════════════════════════════════════════════════════════════

def test_create_enrollment_token():
    """
    测试 POST /api/enrollment-tokens 生成一次性注册 token。

    验证：
      - 用 dependency_overrides 注入 get_user → 返回有效 user_id
      - mock supabase insert 成功
      - 返回的 token 以 "molt_enroll_" 开头
      - 返回 expires_at 字段
    """
    from main import app
    from routes.auth import get_user

    client = TestClient(app)

    # ── 用 FastAPI dependency_overrides 替换 get_user ──
    app.dependency_overrides[get_user] = lambda: "test-user-id-override"

    # ── 构造 enrollment_tokens 表的 insert mock ──
    enroll_insert_chain = _make_mock_chain([{"token": "molt_enroll_abc123"}])
    table_mocks = {
        "enrollment_tokens": MagicMock(),
    }
    table_mocks["enrollment_tokens"].insert.return_value = enroll_insert_chain

    mock_supabase = _build_supabase_mock(table_mocks)

    with patch("app_state.supabase", mock_supabase):
        resp = client.post("/api/enrollment-tokens", json={
            "platform": "test-platform",
            "agent_name": "test-agent",
        })

    # 清理依赖覆盖，避免影响其他测试
    app.dependency_overrides.pop(get_user, None)

    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "token" in data
    assert data["token"].startswith("molt_enroll_"), \
        f"token 应以 'molt_enroll_' 开头，实际: {data['token']}"
    assert "expires_at" in data
    assert data["expires_at"] != ""


# ═══════════════════════════════════════════════════════════════
# 测试 4：列出用户 Agent
# ═══════════════════════════════════════════════════════════════

def test_list_agents():
    """
    测试 GET /api/agents 列出当前用户的所有 Agent。

    验证：
      - 用 dependency_overrides 注入 get_user → 返回有效 user_id
      - mock did_registry 查询返回非空 Agent 列表
      - 返回 200，响应体为长度 > 0 的 JSON 数组
      - 每条记录包含 did、platform、agent_name、status 字段
    """
    from main import app
    from routes.auth import get_user

    client = TestClient(app)

    # ── 用 FastAPI dependency_overrides 替换 get_user ──
    app.dependency_overrides[get_user] = lambda: "test-user-id-override"

    # ── 构造 did_registry 查询返回的 Agent 列表 ──
    agent_rows = [
        {
            "did": "did:web:test.moltable.io:agent:aaaa1111",
            "platform": "hermes",
            "agent_name": "Hermes Agent",
            "status": "active",
            "last_seen_at": "2025-06-01T12:00:00+00:00",
            "created_at": "2025-05-01T00:00:00+00:00",
        },
        {
            "did": "did:web:test.moltable.io:agent:bbbb2222",
            "platform": "claude",
            "agent_name": "Claude Agent",
            "status": "revoked",
            "last_seen_at": None,
            "created_at": "2025-04-15T00:00:00+00:00",
        },
    ]

    did_select_chain = _make_mock_chain(agent_rows)
    did_select_chain.eq.return_value = did_select_chain  # 保持链: .eq() 返回自身
    did_select_chain.order.return_value = did_select_chain
    table_mocks = {
        "did_registry": MagicMock(),
    }
    table_mocks["did_registry"].select.return_value = did_select_chain

    mock_supabase = _build_supabase_mock(table_mocks)

    with patch("routes.agents.supabase", mock_supabase):
        resp = client.get("/api/agents")

    # 清理依赖覆盖
    app.dependency_overrides.pop(get_user, None)

    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text}"
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2, f"期望 2 个 Agent，实际 {len(data)} 个"

    # 验证每条记录的字段
    for agent in data:
        assert "did" in agent
        assert "platform" in agent
        assert "agent_name" in agent
        assert "status" in agent

    # 验证第一条记录的具体内容
    assert data[0]["did"] == "did:web:test.moltable.io:agent:aaaa1111"
    assert data[0]["platform"] == "hermes"
    assert data[0]["status"] == "active"

"""
Integration tests: Sync Code (molt_sync_xxx) endpoints.

Covers:
- GET  /api/auth/sync-code  — generate new code, old codes revoked
- POST /api/auth/sync       — one-time consumption → api_key + user info
- One-time semantics: used / revoked / expired → 409
- Real-SQLite end-to-end: register → generate → consume → replay → regenerate
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """Create a TestClient using the globally mocked app."""
    from main import app
    return TestClient(app)


@pytest.fixture
def table_mocks(mock_supabase: MagicMock):
    """Return a callable get(name) -> per-table MagicMock so query chains don't collide."""
    registry: dict = {}

    def get(name: str):
        if name not in registry:
            registry[name] = MagicMock()
        return registry[name]

    mock_supabase.table.side_effect = get
    yield get
    mock_supabase.table.side_effect = None


def _auth_header(token: str = "test-jwt-token") -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── GET /api/auth/sync-code ──────────────────────────────────

class TestSyncCodeGenerate:
    def test_requires_auth(self, client: TestClient) -> None:
        resp = client.get("/api/auth/sync-code")
        assert resp.status_code == 401

    def test_generate_returns_molt_sync_code(self, client: TestClient,
                                             mock_supabase: MagicMock,
                                             table_mocks) -> None:
        mock_supabase.auth.get_user.return_value.user.id = "uid-001"
        invites = table_mocks("agent_invites")
        invites.update.return_value.eq.return_value.eq.return_value \
            .execute.return_value.data = []
        invites.insert.return_value.execute.return_value.data = [{}]

        resp = client.get("/api/auth/sync-code", headers=_auth_header())
        assert resp.status_code == 200
        body = resp.json()
        assert body["sync_code"].startswith("molt_sync_")
        assert "expires_at" in body

        # 旧码作废：update 必须带 status='revoked'
        update_kwargs = invites.update.call_args[0][0]
        assert update_kwargs["status"] == "revoked"

    def test_regenerate_revokes_old_code(self, client: TestClient,
                                         mock_supabase: MagicMock,
                                         table_mocks) -> None:
        """两次生成 → 第一次的 code 标记 revoked（通过 update 调用断言）。"""
        mock_supabase.auth.get_user.return_value.user.id = "uid-001"
        invites = table_mocks("agent_invites")
        invites.update.return_value.eq.return_value.eq.return_value \
            .execute.return_value.data = []
        invites.insert.return_value.execute.return_value.data = [{}]

        resp1 = client.get("/api/auth/sync-code", headers=_auth_header())
        resp2 = client.get("/api/auth/sync-code", headers=_auth_header())
        assert resp1.status_code == 200 and resp2.status_code == 200
        assert resp1.json()["sync_code"] != resp2.json()["sync_code"]
        # 每次生成都会对旧 pending 码执行 revoked 更新
        assert invites.update.call_count == 2
        for call in invites.update.call_args_list:
            assert call[0][0]["status"] == "revoked"


# ── POST /api/auth/sync ──────────────────────────────────────

class TestSyncConsume:
    def _mock_invite_lookup(self, table_mocks: dict, invite: dict) -> None:
        invites = table_mocks("agent_invites")
        invites.select.return_value.eq.return_value.execute.return_value.data = [invite]
        invites.update.return_value.eq.return_value.eq.return_value \
            .execute.return_value.data = [{"id": "inv-1", "status": "used"}]
        api_keys = table_mocks("api_keys")
        api_keys.insert.return_value.execute.return_value.data = [{}]
        users = table_mocks("users")
        users.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "uid-001", "name": "Alice", "email": "a@b.com"}
        ]

    def test_consume_returns_api_key_and_user(self, client: TestClient,
                                              table_mocks) -> None:
        self._mock_invite_lookup(table_mocks, {
            "id": "inv-1",
            "user_id": "uid-001",
            "status": "pending",
            "expires_at": "2099-01-01T00:00:00+00:00",
        })

        resp = client.post("/api/auth/sync", json={"sync_code": "molt_sync_xxxxxxxxxxxxxxxxxxxxxxxx"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["api_key"].startswith("molt_")
        assert body["user"]["id"] == "uid-001"
        assert body["user"]["name"] == "Alice"
        assert body["user"]["email"] == "a@b.com"

    def test_consume_marks_invite_used(self, client: TestClient,
                                       table_mocks) -> None:
        self._mock_invite_lookup(table_mocks, {
            "id": "inv-1",
            "user_id": "uid-001",
            "status": "pending",
            "expires_at": "2099-01-01T00:00:00+00:00",
        })
        invites = table_mocks("agent_invites")

        client.post("/api/auth/sync", json={"sync_code": "molt_sync_xxxxxxxxxxxxxxxxxxxxxxxx"})
        update_kwargs = invites.update.call_args[0][0]
        assert update_kwargs["status"] == "used"
        assert "used_at" in update_kwargs

    def test_consume_used_code_409(self, client: TestClient,
                                   table_mocks) -> None:
        self._mock_invite_lookup(table_mocks, {
            "id": "inv-1",
            "user_id": "uid-001",
            "status": "used",
            "expires_at": "2099-01-01T00:00:00+00:00",
        })
        resp = client.post("/api/auth/sync", json={"sync_code": "molt_sync_usedcode123456"})
        assert resp.status_code == 409
        assert "已使用" in resp.json()["detail"]

    def test_consume_revoked_code_409(self, client: TestClient,
                                      table_mocks) -> None:
        self._mock_invite_lookup(table_mocks, {
            "id": "inv-1",
            "user_id": "uid-001",
            "status": "revoked",
            "expires_at": "2099-01-01T00:00:00+00:00",
        })
        resp = client.post("/api/auth/sync", json={"sync_code": "molt_sync_revoked123456"})
        assert resp.status_code == 409
        assert "已作废" in resp.json()["detail"]

    def test_consume_expired_code_409(self, client: TestClient,
                                      table_mocks) -> None:
        self._mock_invite_lookup(table_mocks, {
            "id": "inv-1",
            "user_id": "uid-001",
            "status": "pending",
            "expires_at": "2020-01-01T00:00:00+00:00",
        })
        resp = client.post("/api/auth/sync", json={"sync_code": "molt_sync_expired123456"})
        assert resp.status_code == 409
        assert "已过期" in resp.json()["detail"]

    def test_consume_invalid_format_400(self, client: TestClient,
                                        table_mocks) -> None:
        resp = client.post("/api/auth/sync", json={"sync_code": "not-a-sync-code"})
        assert resp.status_code == 400
        assert "格式无效" in resp.json()["detail"]

    def test_consume_unknown_code_404(self, client: TestClient,
                                      table_mocks) -> None:
        invites = table_mocks("agent_invites")
        invites.select.return_value.eq.return_value.execute.return_value.data = []
        resp = client.post("/api/auth/sync", json={"sync_code": "molt_sync_unknown123456"})
        assert resp.status_code == 404


# ── Real-SQLite end-to-end ───────────────────────────────────

@pytest.mark.integration
class TestSyncCodeRealSQLite:
    """用真实 SQLite 适配器验证完整流程（注册 → 生成 → 消费 → 重放 → 重新生成）。"""

    def _make_client(self, tmp_path, monkeypatch) -> TestClient:
        import routes.auth as auth_mod
        from app_state import limiter as _limiter
        from repositories.sqlite_adapter import SQLiteClient, init_schema

        # 速率限制器是进程级单例（内存存储）— 每个测试重置，避免跨测试累积 429
        try:
            _limiter.reset()
        except Exception:
            pass

        db = SQLiteClient(str(tmp_path / "sync_test.db"))
        init_schema(db)
        monkeypatch.setattr(auth_mod, "supabase", db)

        from main import app
        return TestClient(app), db

    def test_full_sync_flow(self, tmp_path, monkeypatch) -> None:
        client, db = self._make_client(tmp_path, monkeypatch)

        # 1. 注册（拿到账号 key）
        reg = client.post("/api/auth/register", json={
            "email": "sync-test@moltable.ai",
            "password": "TestPass2026!",
            "name": "Sync Tester",
        })
        assert reg.status_code == 200, reg.text
        account_key = reg.json()["key"]

        # 2. 生成同步码（需认证）
        gen = client.get("/api/auth/sync-code", headers={"X-API-Key": account_key})
        assert gen.status_code == 200, gen.text
        sync_code = gen.json()["sync_code"]
        assert sync_code.startswith("molt_sync_")

        # 3. 未认证不能生成
        assert client.get("/api/auth/sync-code").status_code == 401

        # 4. 消费 → 返回 api_key + user
        consume = client.post("/api/auth/sync", json={"sync_code": sync_code})
        assert consume.status_code == 200, consume.text
        body = consume.json()
        assert body["api_key"].startswith("molt_")
        assert body["user"]["email"] == "sync-test@moltable.ai"
        recovered_key = body["api_key"]

        # 5. 新 key 立即可用
        me = client.get("/api/auth/me", headers={"X-API-Key": recovered_key})
        assert me.status_code == 200
        assert me.json()["email"] == "sync-test@moltable.ai"

        # 6. 重放 → 409 已使用（一次性）
        replay = client.post("/api/auth/sync", json={"sync_code": sync_code})
        assert replay.status_code == 409
        assert "已使用" in replay.json()["detail"]

        # 7. 生成新码 C（不消费），再生成 D → C 被作废
        code_c = client.get("/api/auth/sync-code", headers={"X-API-Key": account_key}).json()["sync_code"]
        code_d = client.get("/api/auth/sync-code", headers={"X-API-Key": account_key}).json()["sync_code"]
        assert code_c != code_d

        old_try = client.post("/api/auth/sync", json={"sync_code": code_c})
        assert old_try.status_code == 409
        assert "已作废" in old_try.json()["detail"]

        consume2 = client.post("/api/auth/sync", json={"sync_code": code_d})
        assert consume2.status_code == 200, consume2.text
        assert consume2.json()["user"]["id"] == reg.json()["user_id"]

        # 8. 新 key 与账号级 key 指向同一用户
        me2 = client.get("/api/auth/me", headers={"X-API-Key": consume2.json()["api_key"]})
        assert me2.json()["email"] == "sync-test@moltable.ai"

    def test_invalid_and_unknown_codes(self, tmp_path, monkeypatch) -> None:
        client, _ = self._make_client(tmp_path, monkeypatch)

        bad_format = client.post("/api/auth/sync", json={"sync_code": "garbage"})
        assert bad_format.status_code == 400

        unknown = client.post("/api/auth/sync", json={"sync_code": "molt_sync_doesnotexist"})
        assert unknown.status_code == 404

        missing = client.post("/api/auth/sync", json={})
        assert missing.status_code == 422

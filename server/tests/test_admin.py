"""Tests: Admin API — core auth flows. Each test is self-contained."""
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def _make_sb(email="admin@test.com", role="admin"):
    sb = MagicMock()
    sb.table.return_value = sb
    sb.select.return_value = sb
    sb.eq.return_value = sb
    sb.gte.return_value = sb
    sb.ilike.return_value = sb
    sb.order.return_value = sb
    sb.range.return_value = sb
    sb.insert.return_value = sb
    sb.update.return_value = sb
    sb.execute.return_value = MagicMock(data=[{
        "email": email, "password_hash": "mock", "role": role, "is_active": True,
    }], count=1)
    return sb


@pytest.fixture(autouse=True)
def clear_state():
    import services.admin_auth as aa
    aa._failure_store.clear()
    # Force reimport of routes.admin so limiter is fresh
    sys.modules.pop('routes.admin', None)
    yield
    sys.modules.pop('routes.admin', None)


def _client(sb=None):
    """Create a test client with all necessary patches."""
    if sb is None:
        sb = _make_sb()
    patches = [
        patch("app_state.supabase", sb),
        patch("services.admin_auth.supabase", sb),
        patch("routes.admin.supabase", sb),
        patch("services.admin_auth._verify_password", return_value=True),
    ]
    for p in patches:
        p.start()
    import main
    c = TestClient(main.app)
    from services.admin_auth import _failure_store
    _failure_store.clear()
    return c, sb


class TestLogin:
    def test_success(self):
        c, sb = _client()
        r = c.post("/api/admin/login", json={"email": "admin@test.com", "password": "test-password-ok"})
        assert r.status_code == 200, r.text
        assert "token" in r.json()

    def test_wrong_password(self):
        c, sb = _client()
        with patch("services.admin_auth._verify_password", return_value=False):
            r = c.post("/api/admin/login", json={"email": "admin@test.com", "password": "wrong"})
            assert r.status_code == 401

    def test_no_db(self):
        c, sb = _client()
        with patch("services.admin_auth.supabase", None), patch("routes.admin.supabase", None):
            r = c.post("/api/admin/login", json={"email": "x@x.com", "password": "testtesttest"})
            assert r.status_code == 401

    def test_bruteforce_blocks(self):
        c, sb = _client()
        with patch("services.admin_auth._verify_password", return_value=False):
            for i in range(5):
                r = c.post("/api/admin/login", json={"email": "admin@test.com", "password": f"w{i}"})
                assert r.status_code == 401, f"attempt {i}: {r.text}"
            r = c.post("/api/admin/login", json={"email": "admin@test.com", "password": "correct"})
            assert r.status_code == 429, r.text


class TestAuth:
    def test_no_token_rejected(self):
        c, sb = _client()
        assert c.get("/api/admin/stats").status_code == 401
        assert c.get("/api/admin/users").status_code == 401
        assert c.get("/api/admin/health").status_code == 401

    def test_bad_token_rejected(self):
        c, sb = _client()
        h = {"X-Admin-Token": "not-a-real-token"}
        assert c.get("/api/admin/stats", headers=h).status_code == 401
        assert c.get("/api/admin/health", headers=h).status_code == 401

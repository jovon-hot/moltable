"""Tests: Admin API — core auth flows."""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import main


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
def clear_failure_store():
    import services.admin_auth as aa
    aa._failure_store.clear()


# ── Helpers ──

def _patch_app_state(sb=None, is_sqlite=False):
    """Returns list of started patches. Caller must stop() each."""
    import app_state
    import services.admin_auth
    patches = [
        patch.object(app_state, "supabase", sb),
        patch.object(app_state, "_is_sqlite", is_sqlite),
        patch.object(app_state, "get_error_count", return_value=0),
        patch.object(services.admin_auth, "supabase", sb),
    ]
    for p in patches:
        p.start()
    return patches


def _patch_verify(return_val=True):
    """Patch _verify_password to always return return_val."""
    import services.admin_auth
    p = patch.object(services.admin_auth, "_verify_password", return_value=return_val)
    p.start()
    return p


# ═══════════════════════════════════════════════════

class TestLogin:
    def test_success(self):
        aps = _patch_app_state(_make_sb())
        vp = _patch_verify(True)
        try:
            c = TestClient(main.app)
            r = c.post("/api/admin/login", json={"email": "admin@test.com", "password": "p" * 10})
            assert r.status_code == 200, r.text
            assert "token" in r.json()
        finally:
            for p in aps: p.stop()
            vp.stop()

    def test_wrong_password(self):
        aps = _patch_app_state(_make_sb())
        vp = _patch_verify(False)
        try:
            c = TestClient(main.app)
            r = c.post("/api/admin/login", json={"email": "admin@test.com", "password": "wrong"})
            assert r.status_code == 401
        finally:
            for p in aps: p.stop()
            vp.stop()

    def test_no_db(self):
        aps = _patch_app_state(None)
        try:
            c = TestClient(main.app)
            r = c.post("/api/admin/login", json={"email": "x@x.com", "password": "p" * 10})
            assert r.status_code == 401
        finally:
            for p in aps: p.stop()

    def test_bruteforce_blocks(self):
        aps = _patch_app_state(_make_sb())
        vp = _patch_verify(False)
        try:
            c = TestClient(main.app)
            for i in range(5):
                r = c.post("/api/admin/login", json={"email": "admin@test.com", "password": f"w{i}"})
                assert r.status_code == 401, f"attempt {i}: {r.text}"
            r = c.post("/api/admin/login", json={"email": "admin@test.com", "password": "correct"})
            assert r.status_code == 429, r.text
        finally:
            for p in aps: p.stop()
            vp.stop()


class TestAuth:
    def test_no_token_rejected(self):
        aps = _patch_app_state(None)
        try:
            c = TestClient(main.app)
            assert c.get("/api/admin/stats").status_code == 401
            assert c.get("/api/admin/users").status_code == 401
            assert c.get("/api/admin/health").status_code == 401
        finally:
            for p in aps: p.stop()

    def test_bad_token_rejected(self):
        aps = _patch_app_state(None)
        try:
            c = TestClient(main.app)
            h = {"X-Admin-Token": "not-a-real-token"}
            assert c.get("/api/admin/stats", headers=h).status_code == 401
            assert c.get("/api/admin/health", headers=h).status_code == 401
        finally:
            for p in aps: p.stop()

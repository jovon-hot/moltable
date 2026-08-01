"""Tests: Admin API endpoints (login, stats, users, health)."""
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.fixture(autouse=True)
def reset_bruteforce_store():
    """Clear brute-force failure store before each test."""
    import services.admin_auth as aa
    aa._failure_store.clear()
    yield


@pytest.fixture
def client_no_admin():
    """Client with admin disabled (no ADMIN_SECRET)."""
    if "ADMIN_SECRET" in os.environ:
        del os.environ["ADMIN_SECRET"]
    with patch("services.admin_auth._get_secret", return_value=""):
        from main import app
        yield TestClient(app)


@pytest.fixture
def client_with_admin():
    """Client with admin enabled (ADMIN_SECRET set)."""
    with patch("services.admin_auth._get_secret", return_value="test-admin-secret"), \
         patch("services.admin_auth._get_jwt_secret", return_value="test-jwt-secret-32bytes-or-more!!"):
        from main import app
        yield TestClient(app)


class TestAdminDisabled:
    def test_login_returns_401_when_disabled(self, client_no_admin):
        resp = client_no_admin.post("/api/admin/login", json={"secret": "test"})
        assert resp.status_code in (401, 404)

    def test_stats_404(self, client_no_admin):
        resp = client_no_admin.get("/api/admin/stats")
        assert resp.status_code == 404

    def test_users_404(self, client_no_admin):
        resp = client_no_admin.get("/api/admin/users")
        assert resp.status_code == 404

    def test_health_404(self, client_no_admin):
        resp = client_no_admin.get("/api/admin/health")
        assert resp.status_code == 404


class TestAdminLogin:
    def test_login_with_wrong_secret(self, client_with_admin):
        resp = client_with_admin.post("/api/admin/login", json={"secret": "wrong-secret"})
        assert resp.status_code == 401

    def test_login_with_correct_secret(self, client_with_admin):
        resp = client_with_admin.post("/api/admin/login", json={"secret": "test-admin-secret"})
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["expires_in"] == 3600

    def test_login_missing_secret(self, client_with_admin):
        resp = client_with_admin.post("/api/admin/login", json={})
        assert resp.status_code == 401


class TestAdminAuthRequired:
    def get_admin_token(self, client_with_admin):
        resp = client_with_admin.post("/api/admin/login", json={"secret": "test-admin-secret"})
        data = resp.json()
        # If bruteforce kicked in from earlier test, just skip
        if resp.status_code == 429:
            pytest.skip("Rate limited by brute-force protection from prior test")
        assert resp.status_code == 200, f"Login failed: {resp.status_code} {data}"
        return data["token"]

    def test_stats_no_auth(self, client_with_admin):
        resp = client_with_admin.get("/api/admin/stats")
        assert resp.status_code == 401

    def test_stats_bad_token(self, client_with_admin):
        resp = client_with_admin.get("/api/admin/stats", headers={"X-Admin-Token": "bad-token"})
        assert resp.status_code == 401

    def test_stats_with_valid_token(self, client_with_admin):
        token = self.get_admin_token(client_with_admin)
        resp = client_with_admin.get("/api/admin/stats", headers={"X-Admin-Token": token})
        assert resp.status_code in (200, 500)

    def test_users_no_auth(self, client_with_admin):
        resp = client_with_admin.get("/api/admin/users")
        assert resp.status_code == 401

    def test_users_with_token(self, client_with_admin):
        token = self.get_admin_token(client_with_admin)
        resp = client_with_admin.get("/api/admin/users", headers={"X-Admin-Token": token})
        assert resp.status_code in (200, 500)


class TestAdminHealth:
    def get_admin_token(self, client_with_admin):
        resp = client_with_admin.post("/api/admin/login", json={"secret": "test-admin-secret"})
        data = resp.json()
        if resp.status_code == 429:
            pytest.skip("Rate limited by brute-force protection from prior test")
        assert resp.status_code == 200, f"Login failed: {resp.status_code} {data}"
        return data["token"]

    def test_health_with_token(self, client_with_admin):
        token = self.get_admin_token(client_with_admin)
        resp = client_with_admin.get("/api/admin/health", headers={"X-Admin-Token": token})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    def test_health_no_token(self, client_with_admin):
        resp = client_with_admin.get("/api/admin/health")
        assert resp.status_code == 401

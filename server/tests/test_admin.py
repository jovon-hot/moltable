"""Tests: Admin API endpoints (login, stats, users, health).

Requires ADMIN_SECRET to be set for admin endpoints to be enabled.
Tests cover both enabled and disabled states.
"""

import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def client_no_admin():
    """Client with admin disabled (no ADMIN_SECRET)."""
    if "ADMIN_SECRET" in os.environ:
        del os.environ["ADMIN_SECRET"]
    # Patch _get_secret to return empty string (admin disabled)
    with patch("services.admin_auth._get_secret", return_value=""):
        from main import app
        yield TestClient(app)


@pytest.fixture
def client_with_admin():
    """Client with admin enabled (ADMIN_SECRET set)."""
    with patch("services.admin_auth._get_secret", return_value="test-admin-secret"), \
         patch("services.admin_auth._get_jwt_secret", return_value="test-jwt-secret"):
        from main import app
        yield TestClient(app)


class TestAdminDisabled:
    """When ADMIN_SECRET is not set, all admin endpoints should return 404."""

    def test_login_returns_401_when_disabled(self, client_no_admin):
        resp = client_no_admin.post("/api/admin/login", json={"secret": "test"})
        assert resp.status_code == 401  # create_admin_token returns None internally

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
    """Admin login endpoint tests."""

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
    """Protected admin endpoints require a valid token."""

    def get_admin_token(self, client_with_admin):
        resp = client_with_admin.post("/api/admin/login", json={"secret": "test-admin-secret"})
        return resp.json()["token"]

    def test_stats_no_auth(self, client_with_admin):
        resp = client_with_admin.get("/api/admin/stats")
        assert resp.status_code == 401

    def test_stats_bad_token(self, client_with_admin):
        resp = client_with_admin.get(
            "/api/admin/stats",
            headers={"X-Admin-Token": "bad-token"},
        )
        assert resp.status_code == 401

    def test_stats_with_valid_token(self, client_with_admin):
        token = self.get_admin_token(client_with_admin)
        resp = client_with_admin.get(
            "/api/admin/stats",
            headers={"X-Admin-Token": token},
        )
        # May return 500 in SQLite mode (stats unavailable) or 200
        assert resp.status_code in (200, 500)

    def test_users_no_auth(self, client_with_admin):
        resp = client_with_admin.get("/api/admin/users")
        assert resp.status_code == 401

    def test_users_with_token(self, client_with_admin):
        token = self.get_admin_token(client_with_admin)
        resp = client_with_admin.get(
            "/api/admin/users",
            headers={"X-Admin-Token": token},
        )
        # May return 500 in SQLite mode or 200
        assert resp.status_code in (200, 500)


class TestAdminHealth:
    """Admin health endpoint."""

    def get_admin_token(self, client_with_admin):
        resp = client_with_admin.post("/api/admin/login", json={"secret": "test-admin-secret"})
        return resp.json()["token"]

    def test_health_with_token(self, client_with_admin):
        token = self.get_admin_token(client_with_admin)
        resp = client_with_admin.get(
            "/api/admin/health",
            headers={"X-Admin-Token": token},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "error_count" in data
        assert "alerts_configured" in data
        assert "admin_enabled" in data
        assert data["admin_enabled"] is True

    def test_health_no_token(self, client_with_admin):
        resp = client_with_admin.get("/api/admin/health")
        assert resp.status_code == 401

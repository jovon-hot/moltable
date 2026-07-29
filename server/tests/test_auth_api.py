"""
Integration tests: Auth API endpoints.

The global mock supabase in conftest handles auth so endpoints work.
Each test sets up specific mock return values as needed.
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


def _auth_header(token: str = "test-jwt-token") -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestAuthGetUser:
    def test_missing_auth_returns_401(self, client: TestClient) -> None:
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401
        assert "Missing" in resp.json()["detail"]

    def test_get_me_with_token(self, client: TestClient,
                               mock_supabase: MagicMock) -> None:
        mock_supabase.auth.get_user.return_value.user.id = "uid-001"

        user_resp = MagicMock()
        user_resp.data = [{"id": "uid-001", "email": "a@b.com", "name": "Alice",
                           "timezone": "UTC", "language": "en", "created_at": ""}]
        mock_supabase.table.return_value.select.return_value.eq.return_value \
            .execute.return_value = user_resp

        resp = client.get("/api/auth/me", headers=_auth_header())
        assert resp.status_code == 200
        assert resp.json()["id"] == "uid-001"

    def test_get_me_with_api_key(self, client: TestClient,
                                 mock_supabase: MagicMock) -> None:
        key_resp = MagicMock()
        key_resp.data = [{"user_id": "uid-001", "is_active": True}]
        mock_supabase.table.return_value.select.return_value \
            .eq.return_value.execute.return_value = key_resp

        resp = client.get("/api/auth/me", headers={"X-API-Key": "molt_test-key"})
        assert resp.status_code == 200

    def test_get_me_with_invalid_api_key(self, client: TestClient,
                                         mock_supabase: MagicMock) -> None:
        key_resp = MagicMock()
        key_resp.data = []
        mock_supabase.table.return_value.select.return_value \
            .eq.return_value.execute.return_value = key_resp

        resp = client.get("/api/auth/me", headers={"X-API-Key": "molt_wrong-key"})
        assert resp.status_code == 401


class TestAuthAPIKeys:
    def test_create_api_key(self, client: TestClient,
                            mock_supabase: MagicMock) -> None:
        mock_supabase.auth.get_user.return_value.user.id = "uid-001"

        insert_resp = MagicMock()
        insert_resp.data = [{}]
        mock_supabase.table.return_value.insert.return_value \
            .execute.return_value = insert_resp

        resp = client.post(
            "/api/auth/api-keys",
            json={"name": "test-key"},
            headers=_auth_header(),
        )
        assert resp.status_code == 200
        assert resp.json()["key"].startswith("molt_")
        assert resp.json()["name"] == "test-key"

    def test_list_api_keys(self, client: TestClient,
                           mock_supabase: MagicMock) -> None:
        mock_supabase.auth.get_user.return_value.user.id = "uid-001"

        list_resp = MagicMock()
        list_resp.data = [{"id": "k1", "name": "My Key", "key_prefix": "molt_abc",
                           "is_active": True, "created_at": "", "last_used_at": None}]
        mock_supabase.table.return_value.select.return_value \
            .eq.return_value.execute.return_value = list_resp

        resp = client.get("/api/auth/api-keys", headers=_auth_header())
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert resp.json()[0]["name"] == "My Key"

    def test_revoke_api_key(self, client: TestClient,
                            mock_supabase: MagicMock) -> None:
        mock_supabase.auth.get_user.return_value.user.id = "uid-001"

        delete_resp = MagicMock()
        delete_resp.data = [{}]
        mock_supabase.table.return_value.update.return_value \
            .eq.return_value.eq.return_value.execute.return_value = delete_resp

        resp = client.delete(
            "/api/auth/api-keys/k1",
            headers=_auth_header(),
        )
        assert resp.status_code == 200
        assert resp.json()["revoked"] is True

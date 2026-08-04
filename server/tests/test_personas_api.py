"""
Integration tests: Personas API endpoints.

Uses the globally mocked supabase from conftest.
In SQLite mode, personas route skips supabase entirely — patch _is_sqlite to False
so these tests hit the mock as expected.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    # Patch at call time — _is_offline() reads this attr on each call
    import routes.personas as rp
    from main import app
    orig = rp._is_sqlite
    rp._is_sqlite = False
    yield TestClient(app)
    rp._is_sqlite = orig


@pytest.fixture
def auth_header() -> dict:
    return {"Authorization": "Bearer test-token"}


class TestPersonas:
    def test_list_personas_empty(self, client: TestClient,
                                 mock_supabase: MagicMock,
                                 auth_header: dict) -> None:
        mock_supabase.auth.get_user.return_value.user.id = "test-user-001"

        list_resp = MagicMock()
        list_resp.data = []
        mock_supabase.table.return_value.select.return_value \
            .eq.return_value.eq.return_value.execute.return_value = list_resp

        resp = client.get("/api/personas/", headers=auth_header)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_personas_with_data(self, client: TestClient,
                                     mock_supabase: MagicMock,
                                     auth_header: dict) -> None:
        mock_supabase.auth.get_user.return_value.user.id = "test-user-001"

        list_resp = MagicMock()
        list_resp.data = [
            {"id": "p1", "name": "Claude", "type": "constructed",
             "description": "AI", "system_prompt": "", "traits": {},
             "model_preference": "claude", "is_active": True},
        ]
        mock_supabase.table.return_value.select.return_value \
            .eq.return_value.eq.return_value.execute.return_value = list_resp

        resp = client.get("/api/personas/", headers=auth_header)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Claude"

    def test_create_persona(self, client: TestClient,
                            mock_supabase: MagicMock,
                            auth_header: dict) -> None:
        mock_supabase.auth.get_user.return_value.user.id = "test-user-001"

        insert_resp = MagicMock()
        insert_resp.data = [{"id": "p-new"}]
        mock_supabase.table.return_value.insert.return_value \
            .execute.return_value = insert_resp

        resp = client.post(
            "/api/personas/",
            json={
                "name": "New Persona",
                "type": "constructed",
                "description": "Test persona",
                "system_prompt": "You are a test.",
                "traits": {"style": "helpful"},
                "model_preference": "gpt-4",
            },
            headers=auth_header,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["created"] is True
        assert data["id"] == "p-new"

    def test_create_persona_requires_name(self, client: TestClient,
                                          mock_supabase: MagicMock,
                                          auth_header: dict) -> None:
        mock_supabase.auth.get_user.return_value.user.id = "test-user-001"

        resp = client.post(
            "/api/personas/",
            json={"type": "constructed"},
            headers=auth_header,
        )
        assert resp.status_code == 422

    def test_personas_requires_auth(self, client: TestClient) -> None:
        resp = client.get("/api/personas/")
        assert resp.status_code == 401

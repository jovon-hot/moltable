"""Integration tests: Memories API endpoints (CRUD + search).

Uses TestClient with in-memory VectorStore (patched via conftest)."""

from __future__ import annotations
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _clean_store(test_store):
    """Clear the in-memory store before each test."""
    test_store._store.clear()


@pytest.fixture
def client() -> TestClient:
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_header() -> dict:
    return {"Authorization": "Bearer test-token"}


def test_save_memory_success(client, auth_header):
    resp = client.post(
        "/api/memories/",
        json={"content": "Alice likes hiking", "category": "fact"},
        headers=auth_header,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["saved"] is True
    assert "id" in data


def test_save_memory_requires_auth(client):
    resp = client.post("/api/memories/", json={"content": "test"})
    assert resp.status_code == 401


def test_save_memory_validates_category(client, auth_header):
    resp = client.post(
        "/api/memories/",
        json={"content": "test", "category": "invalid-category"},
        headers=auth_header,
    )
    assert resp.status_code == 422


def test_save_memory_empty_content(client, auth_header):
    resp = client.post(
        "/api/memories/",
        json={"content": ""},
        headers=auth_header,
    )
    assert resp.status_code == 422


def test_list_memories(client, auth_header):
    client.post(
        "/api/memories/",
        json={"content": "A fact", "category": "fact"},
        headers=auth_header,
    )
    resp = client.get("/api/memories/", headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert "memories" in data
    assert "total" in data
    assert len(data["memories"]) >= 1


def test_list_memories_categories(client, auth_header):
    client.post(
        "/api/memories/",
        json={"content": "Pref item", "category": "preference"},
        headers=auth_header,
    )
    resp = client.get("/api/memories/?category=preference", headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert "memories" in data
    if data["memories"]:
        assert all(m["category"] == "preference" for m in data["memories"])


def test_get_memory_found(client, auth_header):
    saved = client.post(
        "/api/memories/",
        json={"content": "Specific memory", "category": "fact"},
        headers=auth_header,
    ).json()
    mem_id = saved["id"]

    resp = client.get(f"/api/memories/{mem_id}", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["content"] == "Specific memory"


def test_get_memory_not_found(client, auth_header):
    resp = client.get("/api/memories/nonexistent", headers=auth_header)
    assert resp.status_code == 404


def test_update_memory(client, auth_header):
    saved = client.post(
        "/api/memories/",
        json={"content": "Original", "category": "fact"},
        headers=auth_header,
    ).json()
    mem_id = saved["id"]

    resp = client.put(
        f"/api/memories/{mem_id}",
        json={"content": "Updated"},
        headers=auth_header,
    )
    assert resp.status_code == 200
    assert resp.json()["updated"] is True

    get_resp = client.get(f"/api/memories/{mem_id}", headers=auth_header)
    assert get_resp.json()["content"] == "Updated"


def test_update_memory_not_found(client, auth_header):
    resp = client.put(
        "/api/memories/nonexistent",
        json={"content": "Nope"},
        headers=auth_header,
    )
    assert resp.status_code == 404


def test_update_empty_payload(client, auth_header):
    saved = client.post(
        "/api/memories/",
        json={"content": "Test", "category": "fact"},
        headers=auth_header,
    ).json()
    resp = client.put(
        f"/api/memories/{saved['id']}",
        json={},
        headers=auth_header,
    )
    assert resp.status_code in (400, 422)


def test_delete_memory(client, auth_header):
    saved = client.post(
        "/api/memories/",
        json={"content": "To delete", "category": "fact"},
        headers=auth_header,
    ).json()
    mem_id = saved["id"]

    resp = client.delete(f"/api/memories/{mem_id}", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    get_resp = client.get(f"/api/memories/{mem_id}", headers=auth_header)
    assert get_resp.status_code == 404


def test_delete_memory_not_found(client, auth_header):
    resp = client.delete("/api/memories/nonexistent", headers=auth_header)
    assert resp.status_code == 404


def test_search_memories(client, auth_header):
    client.post(
        "/api/memories/",
        json={"content": "Alice loves hiking", "category": "fact"},
        headers=auth_header,
    )
    resp = client.get("/api/memories/search?q=hiking", headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert "query" in data
    assert "results" in data


def test_search_memories_no_query(client, auth_header):
    resp = client.get("/api/memories/search", headers=auth_header)
    assert resp.status_code == 422

"""
Integration tests: Git-style bidirectional sync endpoints.

Covers:
- POST /api/sync/push    — push new / updated memories, personas, projects
- Conflict detection     — version mismatch -> three-way diff, no silent overwrite
- POST /api/sync/resolve — resolve a conflict -> server accepts with version bump
- POST /api/sync/pull    — pull changes since timestamp / pull all
- POST /api/sync/export  — download all user data as a JSON file
- POST /api/sync/import  — upload and merge a JSON export file
- Empty state / auth requirements

Uses a real SQLite database (following tests/test_sync_code.py pattern):
auth is done via a mocked Supabase JWT lookup so get_user() returns a fixed id,
while the sync route module is pointed at the real SQLite adapter.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

USER_ID = "test-user-id"


@pytest.fixture
def sync_env(tmp_path, monkeypatch):
    """TestClient + real SQLite DB wired into routes.sync."""
    import routes.sync as sync_mod
    from app_state import limiter as _limiter
    from repositories.sqlite_adapter import SQLiteClient, init_schema

    try:
        _limiter.reset()
    except Exception:
        pass

    db = SQLiteClient(str(tmp_path / "sync_test.db"))
    init_schema(db)
    db.table("users").insert({"id": USER_ID, "email": "sync-test@moltable.ai"}).execute()
    monkeypatch.setattr(sync_mod, "supabase", db)

    from main import app

    return TestClient(app), db


@pytest.fixture
def auth_headers(mock_supabase: MagicMock) -> dict:
    """JWT auth header; get_user() resolves to USER_ID via the global mock."""
    mock_supabase.auth.get_user.return_value.user.id = USER_ID
    return {"Authorization": "Bearer test-jwt-token"}


def _push(client: TestClient, headers: dict, **types):
    return client.post(
        "/api/sync/push", json={k: v for k, v in types.items() if v}, headers=headers
    )


def _memory(
    item_id: str, content: str, base_version: int = 0, updated_at: str | None = None
) -> dict:
    item = {"id": item_id, "content": content, "base_version": base_version}
    if updated_at:
        item["updated_at"] = updated_at
    return item


# ── Push ──────────────────────────────────────────────────


class TestPush:
    def test_requires_auth(self, sync_env):
        client, _db = sync_env
        resp = client.post("/api/sync/push", json={"memories": []})
        assert resp.status_code == 401

    def test_push_new_memory(self, sync_env, auth_headers):
        client, db = sync_env
        resp = _push(client, auth_headers, memories=[_memory("mem-1", "hello world")])
        assert resp.status_code == 200
        body = resp.json()
        assert body["conflicts"] == []
        assert len(body["accepted"]) == 1
        assert body["accepted"][0]["id"] == "mem-1"
        assert body["accepted"][0]["type"] == "memory"
        assert body["accepted"][0]["version"] == 1

        rows = (
            db.table("memories").select("*").eq("id", "mem-1").eq("user_id", USER_ID).execute().data
        )
        assert len(rows) == 1
        assert rows[0]["content"] == "hello world"
        assert rows[0]["version"] == 1

    def test_push_updated_memory_bumps_version(self, sync_env, auth_headers):
        client, db = sync_env
        _push(client, auth_headers, memories=[_memory("mem-1", "v1 content")])
        resp = _push(
            client, auth_headers, memories=[_memory("mem-1", "v2 content", base_version=1)]
        )
        assert resp.status_code == 200
        assert resp.json()["conflicts"] == []
        assert resp.json()["accepted"][0]["version"] == 2

        rows = db.table("memories").select("*").eq("id", "mem-1").execute().data
        assert rows[0]["content"] == "v2 content"
        assert rows[0]["version"] == 2
        assert rows[0]["base_content"] == "v1 content"

    def test_push_persona(self, sync_env, auth_headers):
        client, db = sync_env
        resp = _push(
            client,
            auth_headers,
            personas=[
                {
                    "id": "persona-1",
                    "content": {"name": "Alice", "description": "Analytical helper"},
                    "base_version": 0,
                }
            ],
        )
        assert resp.status_code == 200
        assert resp.json()["accepted"][0]["type"] == "persona"

        rows = db.table("personas").select("*").eq("id", "persona-1").execute().data
        assert rows[0]["name"] == "Alice"
        assert rows[0]["description"] == "Analytical helper"
        assert rows[0]["version"] == 1

    def test_push_project(self, sync_env, auth_headers):
        client, db = sync_env
        resp = _push(
            client,
            auth_headers,
            projects=[
                {
                    "id": "proj-1",
                    "content": {
                        "name": "Website",
                        "description": "Marketing site",
                        "tools": ["nextjs", "tailwind"],
                    },
                    "base_version": 0,
                }
            ],
        )
        assert resp.status_code == 200
        assert resp.json()["accepted"][0]["type"] == "project"

        rows = db.table("projects").select("*").eq("id", "proj-1").execute().data
        assert rows[0]["name"] == "Website"
        assert rows[0]["version"] == 1


# ── Conflicts ─────────────────────────────────────────────


class TestConflict:
    def _seed_conflict(self, client, auth_headers):
        """Server row ends at v2; client still edits from v1."""
        _push(client, auth_headers, memories=[_memory("mem-2", "server v1 content")])
        _push(
            client, auth_headers, memories=[_memory("mem-2", "server v2 content", base_version=1)]
        )
        return _push(
            client, auth_headers, memories=[_memory("mem-2", "client edit", base_version=1)]
        )

    def test_push_conflict_returns_three_way_diff(self, sync_env, auth_headers):
        client, _db = sync_env
        resp = self._seed_conflict(client, auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["accepted"] == []
        assert len(body["conflicts"]) == 1

        conflict = body["conflicts"][0]
        assert conflict["id"] == "mem-2"
        assert conflict["type"] == "memory"
        assert conflict["ours"] == "server v2 content"
        assert conflict["base"] == "server v1 content"
        assert conflict["theirs"] == "client edit"
        assert conflict["ours_version"] == 2
        assert conflict["theirs_base_version"] == 1
        assert "<<< ours" in conflict["diff"]
        assert "||| base" in conflict["diff"]
        assert "||| theirs" in conflict["diff"]

    def test_push_conflict_does_not_overwrite_server(self, sync_env, auth_headers):
        client, db = sync_env
        self._seed_conflict(client, auth_headers)
        rows = db.table("memories").select("*").eq("id", "mem-2").execute().data
        assert rows[0]["content"] == "server v2 content"
        assert rows[0]["version"] == 2


# ── Resolve ───────────────────────────────────────────────


class TestResolve:
    def test_resolve_conflict_bumps_version(self, sync_env, auth_headers):
        client, db = sync_env
        TestConflict()._seed_conflict(client, auth_headers)

        resp = client.post(
            "/api/sync/resolve",
            json={
                "id": "mem-2",
                "type": "memory",
                "resolved_content": "merged content",
                "base_version": 2,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["new_version"] == 3

        rows = db.table("memories").select("*").eq("id", "mem-2").execute().data
        assert rows[0]["content"] == "merged content"
        assert rows[0]["version"] == 3
        assert rows[0]["base_content"] == "server v2 content"

    def test_resolve_missing_id_returns_404(self, sync_env, auth_headers):
        client, _db = sync_env
        resp = client.post(
            "/api/sync/resolve",
            json={
                "id": "does-not-exist",
                "type": "memory",
                "resolved_content": "x",
                "base_version": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 404


# ── Pull ──────────────────────────────────────────────────


class TestPull:
    def test_pull_empty_state(self, sync_env, auth_headers):
        client, _db = sync_env
        resp = client.post("/api/sync/pull", json={}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == {"memories": [], "personas": [], "projects": []}

    def test_pull_all_returns_everything(self, sync_env, auth_headers):
        client, _db = sync_env
        _push(
            client,
            auth_headers,
            memories=[_memory("mem-1", "m")],
            personas=[{"id": "p-1", "content": {"name": "Alice"}, "base_version": 0}],
            projects=[{"id": "pr-1", "content": {"name": "Proj"}, "base_version": 0}],
        )

        resp = client.post("/api/sync/pull", json={}, headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["memories"]) == 1
        assert body["memories"][0]["id"] == "mem-1"
        assert body["memories"][0]["content"] == "m"
        assert body["memories"][0]["version"] == 1
        assert body["personas"][0]["content"]["name"] == "Alice"
        assert body["projects"][0]["content"]["name"] == "Proj"

    def test_pull_since_filters_by_updated_at(self, sync_env, auth_headers):
        client, _db = sync_env
        _push(
            client,
            auth_headers,
            memories=[
                _memory("mem-old", "old", updated_at="2026-08-01T00:00:00Z"),
                _memory("mem-new", "new", updated_at="2026-08-11T00:00:00Z"),
            ],
        )

        resp = client.post(
            "/api/sync/pull", json={"since": "2026-08-10T00:00:00Z"}, headers=auth_headers
        )
        assert resp.status_code == 200
        ids = [m["id"] for m in resp.json()["memories"]]
        assert ids == ["mem-new"]


# ── Export / Import ───────────────────────────────────────


class TestExportImport:
    def test_export_returns_all_user_data(self, sync_env, auth_headers):
        client, _db = sync_env
        _push(
            client,
            auth_headers,
            memories=[_memory("mem-1", "m")],
            personas=[{"id": "p-1", "content": {"name": "Alice"}, "base_version": 0}],
        )

        resp = client.post("/api/sync/export", json={}, headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["memories"]) == 1
        assert body["memories"][0]["content"] == "m"
        assert body["personas"][0]["content"]["name"] == "Alice"
        assert "exported_at" in body
        assert body["schema_version"] == 1

    def test_import_creates_new_rows(self, sync_env, auth_headers):
        client, db = sync_env
        resp = client.post(
            "/api/sync/import",
            json={
                "memories": [
                    {
                        "id": "imp-1",
                        "content": "imported",
                        "version": 1,
                        "updated_at": "2026-08-10T00:00:00Z",
                    }
                ],
                "personas": [],
                "projects": [],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json() == {"imported": 1, "updated": 0, "skipped": 0}

        rows = db.table("memories").select("*").eq("id", "imp-1").execute().data
        assert rows[0]["content"] == "imported"
        assert rows[0]["version"] == 1

    def test_import_updates_newer_and_skips_older(self, sync_env, auth_headers):
        client, _db = sync_env
        _push(
            client,
            auth_headers,
            memories=[_memory("imp-2", "server content", updated_at="2026-08-10T00:00:00Z")],
        )

        newer = client.post(
            "/api/sync/import",
            json={
                "memories": [
                    {
                        "id": "imp-2",
                        "content": "newer content",
                        "version": 3,
                        "updated_at": "2026-08-12T00:00:00Z",
                    }
                ],
                "personas": [],
                "projects": [],
            },
            headers=auth_headers,
        )
        assert newer.json() == {"imported": 0, "updated": 1, "skipped": 0}

        older = client.post(
            "/api/sync/import",
            json={
                "memories": [
                    {
                        "id": "imp-2",
                        "content": "older content",
                        "version": 1,
                        "updated_at": "2026-08-01T00:00:00Z",
                    }
                ],
                "personas": [],
                "projects": [],
            },
            headers=auth_headers,
        )
        assert older.json() == {"imported": 0, "updated": 0, "skipped": 1}

        pull = client.post("/api/sync/pull", json={}, headers=auth_headers)
        assert pull.json()["memories"][0]["content"] == "newer content"

"""
Unit tests: SupabaseMemoryRepository — mock-based tests.

All Supabase calls are mocked so tests are fully self-contained
and do not require a live Supabase instance.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from repositories.memory_repo import SupabaseMemoryRepository
from services.vector_store import VectorStore

# ── Fixtures ──────────────────────────────────────────

@pytest.fixture
def fallback() -> VectorStore:
    return VectorStore()


@pytest.fixture
def repo_online(mock_supabase: MagicMock) -> SupabaseMemoryRepository:
    """Repository with a mock Supabase client (online mode)."""
    return SupabaseMemoryRepository(mock_supabase)


@pytest.fixture
def repo_offline(fallback: VectorStore) -> SupabaseMemoryRepository:
    """Repository with supabase=None (offline/fallback mode)."""
    return SupabaseMemoryRepository(None, fallback_store=fallback)


# ── Online mode — mock Supabase ───────────────────────

def test_insert_online_calls_supabase(repo_online: SupabaseMemoryRepository,
                                      mock_supabase: MagicMock,
                                      sample_embedding: list[float]) -> None:
    """insert() should call supabase.table().insert().execute()."""
    mock_resp = MagicMock()
    mock_resp.data = [{
        "id": "abc-123",
        "user_id": "test-user-001",
        "content": "Test",
        "embedding": sample_embedding,
        "category": "fact",
        "source": "manual",
        "confidence": 1.0,
        "tags": [],
        "is_archived": False,
        "created_at": "2025-06-01T00:00:00",
    }]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_resp

    result = repo_online.insert("test-user-001", "Test", sample_embedding)
    assert result["id"] == "abc-123"
    assert result["content"] == "Test"
    mock_supabase.table.assert_called_with("memories")


def test_get_online_returns_none_when_missing(repo_online: SupabaseMemoryRepository,
                                              mock_supabase: MagicMock) -> None:
    """get() should return None when supabase returns no data."""
    mock_resp = MagicMock()
    mock_resp.data = []
    mock_supabase.table.return_value.select.return_value.eq.return_value \
        .eq.return_value.eq.return_value.limit.return_value.execute.return_value = mock_resp

    result = repo_online.get("nonexistent", "test-user-001")
    assert result is None


def test_dict_from_row_parses_json_string_tags(repo_online: SupabaseMemoryRepository) -> None:
    """_dict_from_row() 应把 SQLite 存储的 JSON 字符串 tags 解析为 list (Sprint 2)."""
    row = {
        "id": "abc-1", "user_id": "u1", "content": "带标签的记忆",
        "embedding": "[0.1, 0.2]", "category": "fact", "source": "manual",
        "confidence": 1.0, "tags": '["report", "fost"]',
        "is_archived": False, "created_at": "2025-01-01T00:00:00",
    }
    doc = repo_online._dict_from_row(row)
    assert doc["tags"] == ["report", "fost"]


def test_dict_from_row_tags_none_and_empty(repo_online: SupabaseMemoryRepository) -> None:
    """_dict_from_row() 对缺失/空/空数组字符串 tags 都应返回 []."""
    base = {
        "id": "abc-2", "user_id": "u1", "content": "x",
        "embedding": [], "category": "fact", "source": "manual",
        "confidence": 1.0, "is_archived": False, "created_at": "",
    }
    assert repo_online._dict_from_row({**base, "tags": None})["tags"] == []
    assert repo_online._dict_from_row({**base, "tags": []})["tags"] == []
    assert repo_online._dict_from_row({**base, "tags": "[]"})["tags"] == []


# ── Offline mode — fallback VectorStore ───────────────

def test_insert_offline_uses_fallback(repo_offline: SupabaseMemoryRepository,
                                      sample_embedding: list[float]) -> None:
    """With supabase=None, insert() should delegate to fallback store."""
    result = repo_offline.insert("user-off", "Offline test", sample_embedding)
    assert result["content"] == "Offline test"
    assert result["user_id"] == "user-off"


def test_list_offline_returns_all(repo_offline: SupabaseMemoryRepository,
                                  sample_embedding: list[float]) -> None:
    """list() via fallback should return all memories for that user."""
    repo_offline.insert("u1", "A", sample_embedding)
    repo_offline.insert("u1", "B", sample_embedding)
    repo_offline.insert("u2", "C", sample_embedding)
    results = repo_offline.list("u1")
    assert len(results) == 2


def test_search_offline(repo_offline: SupabaseMemoryRepository) -> None:
    """search() via fallback should use cosine similarity."""
    repo_offline.insert("u1", "Cats", [0.9, 0.1])
    repo_offline.insert("u1", "Dogs", [0.1, 0.9])
    results = repo_offline.search("u1", query_embedding=[0.85, 0.15], top_k=2, threshold=0.5)
    assert len(results) == 1
    assert "Cat" in results[0]["content"]


def test_stats_offline(repo_offline: SupabaseMemoryRepository,
                       sample_embedding: list[float]) -> None:
    """stats() via fallback should report correct counts."""
    r = repo_offline
    a = r.insert("u1", "A", sample_embedding)
    r.insert("u1", "B", sample_embedding)
    r.delete(a["id"], "u1")
    s = r.stats("u1")
    assert s["total"] == 1
    assert s["archived"] == 1


# ── Edge cases ───────────────────────────────────────

def test_delete_online_calls_update(repo_online: SupabaseMemoryRepository,
                                    mock_supabase: MagicMock) -> None:
    """Delete online should call supabase.update({is_archived: True})."""
    mock_resp = MagicMock()
    mock_resp.data = [{"id": "mem-1"}]
    mock_supabase.table.return_value.update.return_value.eq.return_value \
        .eq.return_value.execute.return_value = mock_resp

    result = repo_online.delete("mem-1", "test-user-001")
    assert result is True
    # Verify the update payload contains is_archived
    call_kwargs = mock_supabase.table.return_value.update.call_args[0][0]
    assert call_kwargs["is_archived"] is True

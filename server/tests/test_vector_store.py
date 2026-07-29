"""
Unit tests: VectorStore — in-memory CRUD + semantic search.

Tests the VectorStore class directly with no external dependencies.
"""

from __future__ import annotations

import math
from typing import List
from services.vector_store import VectorStore, _cosine


# ── Cosine similarity helper ───────────────────────────

def test_cosine_similarity_identical() -> None:
    """Two identical vectors should have similarity = 1.0."""
    a = [1.0, 0.0, 0.0]
    assert _cosine(a, a) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal() -> None:
    """Orthogonal vectors should have similarity = 0.0."""
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert _cosine(a, b) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector() -> None:
    """A zero vector should return 0.0 (not divide-by-zero)."""
    assert _cosine([0.0, 0.0], [1.0, 0.0]) == pytest.approx(0.0)
    assert _cosine([1.0, 0.0], [0.0, 0.0]) == pytest.approx(0.0)


def test_cosine_similarity_partial() -> None:
    """Vectors at 45° should have similarity ≈ 0.7071."""
    a = [1.0, 0.0]
    b = [1.0, 1.0]
    expected = 1.0 / math.sqrt(2)
    assert _cosine(a, b) == pytest.approx(expected, rel=1e-4)


# ── VectorStore CRUD ──────────────────────────────────

def test_insert_and_get() -> None:
    """Insert a memory and retrieve it by id."""
    vs = VectorStore()
    inserted = vs.insert("user1", "Hello world", [0.1, 0.2, 0.3])
    doc = vs.get(inserted["id"], "user1")
    assert doc is not None
    assert doc["content"] == "Hello world"
    assert doc["user_id"] == "user1"
    assert doc["is_archived"] is False


def test_get_wrong_user_returns_none() -> None:
    """A memory from user1 should not be visible to user2."""
    vs = VectorStore()
    inserted = vs.insert("user1", "Secret data", [0.1, 0.2])
    assert vs.get(inserted["id"], "user2") is None


def test_get_archived_returns_none() -> None:
    """An archived memory should not be returned by get()."""
    vs = VectorStore()
    inserted = vs.insert("user1", "Archived soon", [0.1, 0.2])
    vs.delete(inserted["id"], "user1")
    assert vs.get(inserted["id"], "user1") is None


def test_list_by_user() -> None:
    """list() should return only the requesting user's memories."""
    vs = VectorStore()
    vs.insert("user1", "Mem1", [0.1])
    vs.insert("user1", "Mem2", [0.2])
    vs.insert("user2", "Mem3", [0.3])
    results = vs.list("user1")
    assert len(results) == 2
    assert all(r["user_id"] == "user1" for r in results)


def test_list_by_category() -> None:
    """list() should filter by category when specified."""
    vs = VectorStore()
    vs.insert("user1", "Fact 1", [0.1], category="fact")
    vs.insert("user1", "Pref 1", [0.2], category="preference")
    results = vs.list("user1", category="fact")
    assert len(results) == 1
    assert results[0]["category"] == "fact"


def test_list_respects_limit() -> None:
    """list() should not return more than limit items."""
    vs = VectorStore()
    for i in range(10):
        vs.insert("user1", f"Mem {i}", [0.1 * i])
    assert len(vs.list("user1", limit=3)) == 3


def test_update() -> None:
    """Update should modify fields on an existing memory."""
    vs = VectorStore()
    inserted = vs.insert("user1", "Original", [0.1, 0.2])
    assert vs.update(inserted["id"], "user1", content="Updated")
    doc = vs.get(inserted["id"], "user1")
    assert doc["content"] == "Updated"


def test_update_wrong_user_fails() -> None:
    """Update by a different user should return False."""
    vs = VectorStore()
    inserted = vs.insert("user1", "Original", [0.1])
    assert vs.update(inserted["id"], "user2", content="Nope") is False


def test_update_nonexistent_fails() -> None:
    """Update on an unknown id should return False."""
    vs = VectorStore()
    assert vs.update("nonexistent", "user1", content="X") is False


def test_delete_soft_deletes() -> None:
    """Delete should set is_archived=True, not remove the doc."""
    vs = VectorStore()
    inserted = vs.insert("user1", "To delete", [0.1])
    assert vs.delete(inserted["id"], "user1") is True
    # Document still in store but marked archived
    doc_internal = vs._store[inserted["id"]]
    assert doc_internal["is_archived"] is True


def test_delete_wrong_user_fails() -> None:
    """Delete by a different user should return False."""
    vs = VectorStore()
    inserted = vs.insert("user1", "Mine", [0.1])
    assert vs.delete(inserted["id"], "user2") is False


# ── VectorStore Search ────────────────────────────────

def test_search_by_similarity() -> None:
    """search() should return the most similar memories above threshold."""
    vs = VectorStore()
    vs.insert("user1", "I love cats", [0.9, 0.1])
    vs.insert("user1", "I love dogs", [0.8, 0.2])
    vs.insert("user1", "Python programming", [0.1, 0.9])
    results = vs.search("user1", query_embedding=[0.85, 0.15], top_k=2, threshold=0.5)
    assert len(results) == 2
    assert results[0]["similarity"] >= results[1]["similarity"]


def test_search_respects_category_filter() -> None:
    """search() should narrow results by category."""
    vs = VectorStore()
    vs.insert("user1", "Cats are great", [0.9, 0.1], category="preference")
    vs.insert("user1", "Dogs are great", [0.9, 0.1], category="fact")
    results = vs.search("user1", [0.9, 0.1], category="preference")
    assert all(r["category"] == "preference" for r in results)


def test_search_excludes_archived() -> None:
    """Archived memories should not appear in search results."""
    vs = VectorStore()
    inserted = vs.insert("user1", "Old fact", [0.9, 0.1])
    vs.delete(inserted["id"], "user1")
    results = vs.search("user1", [0.9, 0.1])
    assert len(results) == 0


def test_find_conflicts() -> None:
    """find_conflicts should return near-duplicates (sim > 0.85)."""
    vs = VectorStore()
    vs.insert("user1", "I like apples", [0.9, 0.1])
    vs.insert("user1", "I love apples", [0.88, 0.12])
    vs.insert("user1", "I hate apples", [0.1, 0.9])
    conflicts = vs.find_conflicts("user1", [0.89, 0.11])
    assert len(conflicts) >= 1
    # All returned similarities should be >= 0.85
    assert all(c["similarity"] >= 0.85 for c in conflicts)


def test_stats() -> None:
    """stats() should return correct total and archived counts."""
    vs = VectorStore()
    a = vs.insert("user1", "A", [0.1])
    vs.insert("user1", "B", [0.2])
    vs.insert("user1", "C", [0.3])
    vs.delete(a["id"], "user1")
    s = vs.stats("user1")
    assert s["total"] == 2  # B, C
    assert s["archived"] == 1  # A


import pytest

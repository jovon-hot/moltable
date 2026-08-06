"""Tests for Memory Insight Engine — automatic consolidation & pattern discovery."""

import pytest
from unittest.mock import patch, MagicMock

# ── Test clustering ──────────────────────────────────────

from services.memory_insights import (
    cluster_memories,
    detect_patterns,
    _cosine_similarity,
    _generate_insight_fallback,
)


class TestCosineSimilarity:
    def test_identical_vectors(self):
        v = [1.0, 2.0, 3.0]
        assert _cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        assert _cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        a = [1.0, 1.0, 1.0]
        b = [-1.0, -1.0, -1.0]
        assert _cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_different_lengths(self):
        assert _cosine_similarity([1.0, 2.0], [1.0]) == 0.0

    def test_zero_vector(self):
        assert _cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0

    def test_partial_similarity(self):
        a = [1.0, 0.5, 0.0]
        b = [1.0, 0.5, 0.1]
        assert _cosine_similarity(a, b) > 0.95


class TestClusterMemories:
    def test_empty_list(self):
        assert cluster_memories([]) == []

    def test_single_memory(self):
        memories = [_make_memory("a", [1.0, 0.0])]
        assert cluster_memories(memories) == []

    def test_two_similar_memories(self):
        memories = [
            _make_memory("a", [1.0, 0.5, 0.0]),
            _make_memory("b", [1.0, 0.5, 0.01]),
        ]
        clusters = cluster_memories(memories, threshold=0.9)
        assert len(clusters) == 1
        assert len(clusters[0]) == 2

    def test_two_dissimilar_memories(self):
        memories = [
            _make_memory("a", [1.0, 0.0, 0.0]),
            _make_memory("b", [0.0, 1.0, 0.0]),
        ]
        clusters = cluster_memories(memories)
        assert len(clusters) == 0

    def test_three_with_one_pair(self):
        memories = [
            _make_memory("a", [1.0, 0.5, 0.0]),
            _make_memory("b", [1.0, 0.5, 0.01]),  # similar to a
            _make_memory("c", [0.0, 1.0, 0.0]),   # different
        ]
        clusters = cluster_memories(memories, threshold=0.9)
        assert len(clusters) == 1
        assert len(clusters[0]) == 2
        ids = {m["id"] for m in clusters[0]}
        assert ids == {"a", "b"}

    def test_two_separate_clusters(self):
        memories = [
            _make_memory("a1", [1.0, 0.1, 0.0]),
            _make_memory("a2", [1.0, 0.1, 0.01]),
            _make_memory("b1", [0.0, 1.0, 0.1]),
            _make_memory("b2", [0.01, 1.0, 0.1]),
        ]
        clusters = cluster_memories(memories, threshold=0.9)
        assert len(clusters) == 2
        assert all(len(c) == 2 for c in clusters)

    def test_transitive_clustering(self):
        # a1 similar to a2, a2 similar to a3, a1 not similar to a3
        # Transitive via union-find → all in one cluster
        memories = [
            _make_memory("a1", [1.0, 0.0, 0.0]),
            _make_memory("a2", [1.0, 0.01, 0.0]),   # sim to a1
            _make_memory("a3", [1.0, 0.01, 0.01]),   # sim to a2 but not a1
        ]
        clusters = cluster_memories(memories, threshold=0.999)
        # a1↔a2 pass; a2↔a3 pass; they should all merge transitively
        assert len(clusters) == 1
        assert len(clusters[0]) == 3

    def test_max_cluster_size_capped(self):
        # Create 30 nearly-identical memories
        memories = [
            _make_memory(str(i), [1.0 + i * 0.0001, 0.0, 0.0])
            for i in range(30)
        ]
        clusters = cluster_memories(memories)
        assert len(clusters) == 1
        # Should be capped at MAX_CLUSTER_SIZE = 15
        assert len(clusters[0]) <= 15

    def test_memory_without_embedding_skipped(self):
        memories = [
            _make_memory("a", [1.0, 0.5, 0.0]),
            {"id": "b", "content": "no embedding", "category": "fact"},
            _make_memory("c", [1.0, 0.5, 0.01]),
        ]
        clusters = cluster_memories(memories, threshold=0.9)
        assert len(clusters) == 1
        ids = {m["id"] for m in clusters[0]}
        assert ids == {"a", "c"}


class TestDetectPatterns:
    def test_empty_list(self):
        assert detect_patterns([]) == []

    def test_too_few_memories(self):
        memories = [_make_memory("a")]
        assert detect_patterns(memories) == []

    def test_preference_pattern(self):
        memories = [
            _make_memory("1", content="User likes Python programming"),
            _make_memory("2", content="User prefers dark mode themes"),
            _make_memory("3", content="User favorite color is blue"),
            _make_memory("4", content="User enjoys hiking on weekends"),
            _make_memory("5", content="Random unrelated fact"),
        ]
        patterns = detect_patterns(memories)
        theme_names = {p["theme"] for p in patterns}
        assert "preference" in theme_names
        pref = next(p for p in patterns if p["theme"] == "preference")
        assert pref["keyword_hits"] >= 2

    def test_habit_pattern(self):
        memories = [
            _make_memory("1", content="User always drinks coffee in the morning"),
            _make_memory("2", content="User never misses standup"),
            _make_memory("3", content="User usually works from home on Fridays"),
            _make_memory("4", content="Random fact"),
            _make_memory("5", content="Another random fact"),
        ]
        patterns = detect_patterns(memories)
        theme_names = {p["theme"] for p in patterns}
        assert "habit" in theme_names

    def test_no_patterns(self):
        memories = [
            _make_memory("1", content="The sky is blue"),
            _make_memory("2", content="Water boils at 100°C"),
            _make_memory("3", content="Earth orbits the Sun"),
            _make_memory("4", content="Python is a programming language"),
            _make_memory("5", content="Tokyo is in Japan"),
        ]
        patterns = detect_patterns(memories)
        assert patterns == []

    def test_chinese_keywords(self):
        memories = [
            _make_memory("1", content="用戶喜歡吃辣"),
            _make_memory("2", content="用戶每天跑步"),
            _make_memory("3", content="用戶的目標是升職"),
            _make_memory("4", content="用戶擅長Python"),
            _make_memory("5", content="一些隨機事實"),
        ]
        patterns = detect_patterns(memories)
        # Should detect至少: preference, habit, goal, skill
        themes = {p["theme"] for p in patterns}
        assert "preference" in themes or "goal" in themes or "skill" in themes


class TestInsightFallback:
    def test_fallback_basic(self):
        memories = [
            {"id": "a", "content": "User works at Acme Corp as an engineer", "category": "fact", "source": "manual"},
            {"id": "b", "content": "User's team uses React for frontend", "category": "fact", "source": "agent"},
        ]
        result = _generate_insight_fallback(memories)
        assert "Auto-insight" in result
        assert "Acme Corp" in result
        assert "Related context" in result or "React" in result

    def test_fallback_single(self):
        memories = [{"id": "a", "content": "Solo memory", "category": "fact", "source": "manual"}]
        result = _generate_insight_fallback(memories)
        assert "Solo memory" in result


class TestGenerateInsights:
    """Integration-style tests for the full generate_insights pipeline."""

    def test_not_enough_memories(self):
        from services.memory_insights import generate_insights
        store = _mock_store(1)
        result = generate_insights("user1", store)
        assert result["insights_created"] == 0
        assert "Need at least 2 memories" in result.get("message", "")

    def test_no_clusters_found(self):
        from services.memory_insights import generate_insights
        # Create memories with orthogonal embeddings → no clusters
        memories = [
            {"id": f"m{i}", "content": f"memory {i}", "category": "fact",
             "is_archived": False, "embedding": _unit_vec(i, 384), "source": "test",
             "tags": [], "created_at": "2026-08-01T00:00:00Z"}
            for i in range(10)
        ]
        store = _mock_store_from_list(memories)
        result = generate_insights("user1", store)
        assert result["insights_created"] == 0
        assert result["clusters_found"] == 0

    @patch("services.embedding.embed")
    def test_generates_insights_for_clusters(self, mock_embed):
        from services.memory_insights import generate_insights
        mock_embed.return_value = [0.1] * 384

        # Create two clusters of very similar memories
        base_a = [1.0, 0.5, 0.2] + [0.0] * 381
        base_b = [0.0, 0.0, 0.0, 1.0, 0.5, 0.2] + [0.0] * 378

        memories_a = [
            {"id": f"a{i}", "content": f"User uses Python {i}", "category": "fact",
             "is_archived": False, "embedding": [v + i * 0.0001 for v in base_a],
             "source": "test", "tags": ["python"], "created_at": "2026-08-01T00:00:00Z"}
            for i in range(3)
        ]
        memories_b = [
            {"id": f"b{i}", "content": f"User lives in Berlin {i}", "category": "fact",
             "is_archived": False, "embedding": [v + i * 0.0001 for v in base_b],
             "source": "test", "tags": ["location"], "created_at": "2026-08-01T00:00:00Z"}
            for i in range(3)
        ]
        store = _mock_store_from_list(memories_a + memories_b)
        result = generate_insights("user1", store)
        # At least one cluster should produce an insight
        assert result["insights_created"] >= 1
        assert result["clusters_found"] >= 1
        assert len(result["insights"]) >= 1

    @patch("services.embedding.embed")
    def test_persona_filtering(self, mock_embed):
        from services.memory_insights import generate_insights
        mock_embed.return_value = [0.1] * 384

        memories = [
            {"id": f"p1_{i}", "content": f"Dev stuff {i}", "category": "fact",
             "is_archived": False, "embedding": [1.0, 0.1, 0.0] + [0.0] * 381,
             "persona_id": "dev", "source": "test", "tags": [],
             "created_at": "2026-08-01T00:00:00Z"}
            for i in range(3)
        ] + [
            {"id": f"p2_{i}", "content": f"PM stuff {i}", "category": "fact",
             "is_archived": False, "embedding": [0.0, 1.0, 0.1] + [0.0] * 381,
             "persona_id": "pm", "source": "test", "tags": [],
             "created_at": "2026-08-01T00:00:00Z"}
            for i in range(3)
        ]
        store = _mock_store_from_list(memories)
        result = generate_insights("user1", store, persona_id="dev")
        # Should only scan dev memories (3), threshold may or may not produce clusters
        assert result["total_memories_scanned"] == 3

    def test_archived_excluded(self):
        from services.memory_insights import generate_insights
        memories = [
            {"id": "m0", "content": "archived", "category": "fact",
             "is_archived": True, "embedding": [1.0, 0.0] + [0.0] * 382,
             "source": "test", "tags": [], "created_at": "2026-08-01T00:00:00Z"},
        ]
        store = _mock_store_from_list(memories)
        result = generate_insights("user1", store)
        assert result["total_memories_scanned"] == 0

    def test_insights_excluded_from_reprocessing(self):
        from services.memory_insights import generate_insights
        memories = [
            {"id": "i1", "content": "Old insight", "category": "insight",
             "is_archived": False, "embedding": [1.0, 0.0] + [0.0] * 382,
             "source": "auto", "tags": [], "created_at": "2026-08-01T00:00:00Z"},
        ]
        store = _mock_store_from_list(memories)
        result = generate_insights("user1", store)
        assert result["total_memories_scanned"] == 0  # insight category excluded


# ── Helpers ──────────────────────────────────────────────

def _make_memory(id_: str, embedding: list[float] | None = None,
                 content: str = "test", category: str = "fact",
                 source: str = "test") -> dict:
    emb = embedding or [1.0, 0.0, 0.0]
    return {
        "id": id_,
        "content": content,
        "category": category,
        "is_archived": False,
        "embedding": emb,
        "source": source,
        "tags": [],
        "created_at": "2026-08-01T00:00:00Z",
    }


def _unit_vec(dim: int, total: int) -> list[float]:
    """Create a unit vector with 1.0 at position dim."""
    v = [0.0] * total
    v[dim % total] = 1.0
    return v


def _mock_store(count: int = 5) -> MagicMock:
    """Mock store with N diverse memories."""
    memories = [
        _make_memory(str(i), embedding=_unit_vec(i, 384))
        for i in range(count)
    ]
    return _mock_store_from_list(memories)


def _mock_store_from_list(memories: list[dict]) -> MagicMock:
    store = MagicMock()
    store.list.return_value = memories

    def insert(user_id, content, embedding, *, category, source, confidence, tags, persona_id=None):
        return {
            "id": f"insight_{len(memories)}",
            "content": content,
            "category": category,
        }
    store.insert = insert
    return store

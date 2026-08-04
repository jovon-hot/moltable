"""Tests for memory health & staleness scoring service."""
import pytest
from services.memory_health import (
    compute_health_score,
    generate_health_report,
    HealthReport,
    _compute_age_days,
    _detect_contradiction_signals,
    _find_duplicate_groups,
)
from services.vector_store import VectorStore


class TestAgeComputation:
    def test_none_for_empty(self):
        assert _compute_age_days("") is None

    def test_none_for_invalid(self):
        assert _compute_age_days("not-a-date") is None

    def test_valid_iso_date(self):
        import time
        from datetime import datetime, timezone, timedelta
        # Create timestamp from 5 days ago
        dt = datetime.now(timezone.utc) - timedelta(days=5)
        age = _compute_age_days(dt.isoformat())
        assert age is not None
        assert 4.9 <= age <= 5.1  # ~5 days


class TestContradictionDetection:
    def test_no_contradiction_normal(self):
        assert not _detect_contradiction_signals(
            "I like coffee",
            "The weather is nice today"
        )

    def test_contradiction_with_negation(self):
        assert _detect_contradiction_signals(
            "I prefer using Python for backend development",
            "I no longer prefer using Python for backend development"
        )

    def test_contradiction_with_changed(self):
        assert _detect_contradiction_signals(
            "My favorite color is blue",
            "My favorite color changed from blue to green"
        )

    def test_no_contradiction_different_topics(self):
        assert not _detect_contradiction_signals(
            "I like Python programming",
            "I no longer eat meat"  # Different topic
        )


class TestHealthScoring:
    def test_fresh_memory_scores_high(self):
        from datetime import datetime, timezone
        mem = {
            "id": "test-1",
            "content": "This is a well-formed memory with sufficient length to be considered complete",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "embedding": [0.1] * 384,
        }
        result = compute_health_score(mem, [], None)
        assert result["score"] >= 90
        assert result["recommendation"] == "keep"

    def test_old_memory_scores_low(self):
        from datetime import datetime, timezone, timedelta
        old_date = datetime.now(timezone.utc) - timedelta(days=120)
        mem = {
            "id": "test-2",
            "content": "Some old fact that might be outdated now",
            "created_at": old_date.isoformat(),
            "embedding": [0.2] * 384,
        }
        result = compute_health_score(mem, [], None)
        assert result["score"] < 80
        assert any("old" in f or "aging" in f for f in result["flags"])

    def test_short_memory_flagged(self):
        from datetime import datetime, timezone
        mem = {
            "id": "test-3",
            "content": "ok",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "embedding": [0.3] * 384,
        }
        result = compute_health_score(mem, [], None)
        assert "too_short" in result["flags"]
        assert result["recommendation"] == "enrich"


class TestDuplicateDetection:
    def test_finds_duplicate_groups(self):
        # Create two nearly-identical memories
        mems = [
            {
                "id": "a",
                "content": "User likes Python",
                "embedding": [0.1] * 384,
            },
            {
                "id": "b",
                "content": "User likes Python programming",
                "embedding": [0.1] * 384,  # Same embedding = identical
            },
        ]
        groups = _find_duplicate_groups(mems)
        assert len(groups) >= 1

    def test_no_duplicates_for_unique(self):
        import random
        mems = [
            {
                "id": f"m-{i}",
                "content": f"Memory {i}",
                "embedding": [random.random() for _ in range(384)],
            }
            for i in range(5)
        ]
        groups = _find_duplicate_groups(mems)
        # Random embeddings unlikely to collide at 0.85 threshold
        assert len(groups) <= 2


class TestHealthReport:
    def test_empty_store_returns_zero(self):
        store = VectorStore()
        report = generate_health_report("user-1", store)
        assert isinstance(report, HealthReport)
        assert report.total == 0
        assert report.average_health == 0.0

    def test_report_with_memories(self):
        from datetime import datetime, timezone, timedelta
        store = VectorStore()

        # Add memories with different content quality
        store.insert("user-1", "Fresh and healthy memory with good detail", [0.1]*384,
                     category="fact", source="test")
        store.insert("user-1", "Old stale memory content that has been around", [0.9]*384,
                     category="fact", source="test")
        store.insert("user-1", "short", [0.5]*384,
                     category="fact", source="test")

        report = generate_health_report("user-1", store)
        assert report.total == 3
        assert report.average_health > 0
        # The short one should be flagged for incompleteness
        assert report.incomplete >= 1
        assert len(report.recommendations) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

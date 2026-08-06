"""Tests for relationship inference engine."""
from __future__ import annotations

import pytest
from services.relationship_inference import (
    infer_relationships,
    _extract_key_value_pairs,
    _has_contradiction_signals,
    _count_negations,
    _detect_fact_conflict,
    relationship_impact_score,
    relationship_summary,
    sanitize_relationship_data,
    SUPERSEDE_SIMILARITY,
    CONTRADICT_SIMILARITY,
)


# ── Mock similarity function ────────────────────────────────
def _mock_similarity(text_a: str, text_b: str) -> float:
    """Simple word-overlap similarity for testing."""
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


# ── Key-value pair extraction tests ─────────────────────────
class TestKeyValueExtraction:
    def test_extracts_uses(self):
        pairs = _extract_key_value_pairs("User uses Python for backend development")
        assert ("uses", "python for backend development") in pairs

    def test_extracts_lives_in(self):
        pairs = _extract_key_value_pairs("User lives in San Francisco")
        # "lives" is captured as key, "in San Francisco" as value
        has_lives = any(
            k in ("lives", "lives in") and "francisco" in v.lower()
            for k, v in pairs
        )
        assert has_lives

    def test_extracts_prefers(self):
        pairs = _extract_key_value_pairs("User prefers dark mode themes")
        has_prefers = any(k == "prefers" and "dark mode themes" in v for k, v in pairs)
        assert has_prefers

    def test_extracts_multiple(self):
        pairs = _extract_key_value_pairs(
            "User uses TypeScript and prefers React over Vue"
        )
        assert len(pairs) >= 1

    def test_empty_text(self):
        pairs = _extract_key_value_pairs("")
        assert pairs == []


# ── Contradiction signal detection tests ────────────────────
class TestContradictionSignals:
    def test_detects_actually(self):
        assert _has_contradiction_signals(
            "Actually, it's not right. The user uses TypeScript."
        )

    def test_detects_no_longer(self):
        assert _has_contradiction_signals(
            "The user no longer works at Google."
        )

    def test_detects_correction(self):
        assert _has_contradiction_signals(
            "Correction: the preferred language is Python, not JavaScript."
        )

    def test_no_signal_in_neutral(self):
        assert not _has_contradiction_signals(
            "The user enjoys coding in Python and building web apps."
        )

    def test_detects_chinese_contradiction(self):
        assert _has_contradiction_signals(
            "不对，实际上用户使用的是 TypeScript。"
        )


# ── Negation counting tests ────────────────────────────────
class TestNegationCounting:
    def test_counts_not(self):
        assert _count_negations("This is not correct and I don't agree") >= 2

    def test_zero_negations(self):
        assert _count_negations("This is absolutely correct and I agree") == 0

    def test_counts_chinese(self):
        assert _count_negations("这不是对的，他没有使用JavaScript") >= 2


# ── Fact conflict detection tests ───────────────────────────
class TestFactConflict:
    def test_detects_same_key_different_value(self):
        pairs_a = [("uses", "python")]
        pairs_b = [("uses", "typescript")]
        conflict = _detect_fact_conflict(pairs_a, pairs_b)
        assert conflict == ("uses", "python", "typescript")

    def test_no_conflict_same_value(self):
        pairs_a = [("uses", "python")]
        pairs_b = [("uses", "python")]
        conflict = _detect_fact_conflict(pairs_a, pairs_b)
        assert conflict is None

    def test_no_conflict_different_keys(self):
        pairs_a = [("uses", "python")]
        pairs_b = [("lives", "beijing")]
        conflict = _detect_fact_conflict(pairs_a, pairs_b)
        assert conflict is None

    def test_no_conflict_empty(self):
        conflict = _detect_fact_conflict([], [])
        assert conflict is None


# ── Relationship inference tests ────────────────────────────
class TestInferRelationships:
    def test_supersedes_high_similarity(self):
        new_mem = {
            "id": "mem-2",
            "content": "User uses Python for backend development with FastAPI framework",
            "created_at": "2026-08-07T00:00:00",
        }
        existing = [
            {
                "id": "mem-1",
                "content": "User uses Python for backend development with FastAPI",
                "created_at": "2026-08-01T00:00:00",
            }
        ]
        result = infer_relationships(new_mem, existing, _mock_similarity)
        assert len(result["supersedes"]) >= 1
        assert result["supersedes"][0]["id"] == "mem-1"

    def test_contradicts_with_fact_conflict(self):
        new_mem = {
            "id": "mem-2",
            "content": "User uses TypeScript for frontend development",
            "created_at": "2026-08-07T00:00:00",
        }
        existing = [
            {
                "id": "mem-1",
                "content": "User uses JavaScript for frontend development",
                "created_at": "2026-08-01T00:00:00",
            }
        ]
        result = infer_relationships(new_mem, existing, _mock_similarity)
        assert len(result["contradicts"]) >= 1

    def test_extends_moderate_similarity(self):
        new_mem = {
            "id": "mem-2",
            "content": "User also uses Docker for Python backend containerization",
            "created_at": "2026-08-07T00:00:00",
        }
        existing = [
            {
                "id": "mem-1",
                "content": "User uses Python for backend development",
                "created_at": "2026-08-01T00:00:00",
            }
        ]
        result = infer_relationships(new_mem, existing, _mock_similarity)
        assert len(result["extends"]) >= 1

    def test_no_relationships_low_similarity(self):
        new_mem = {
            "id": "mem-2",
            "content": "User enjoys hiking on weekends in the mountains",
            "created_at": "2026-08-07T00:00:00",
        }
        existing = [
            {
                "id": "mem-1",
                "content": "User uses Python for backend development",
                "created_at": "2026-08-01T00:00:00",
            }
        ]
        result = infer_relationships(new_mem, existing, _mock_similarity)
        assert result["supersedes"] == []
        assert result["contradicts"] == []
        assert result["extends"] == []

    def test_no_similarity_func_returns_empty(self):
        new_mem = {
            "id": "mem-2",
            "content": "User uses Python for backend development",
            "created_at": "2026-08-07T00:00:00",
        }
        existing = [
            {
                "id": "mem-1",
                "content": "User uses Python for backend development",
                "created_at": "2026-08-01T00:00:00",
            }
        ]
        result = infer_relationships(new_mem, existing, None)
        # Without similarity func, only pattern detection works
        assert isinstance(result["supersedes"], list)
        assert isinstance(result["contradicts"], list)
        assert isinstance(result["extends"], list)

    def test_skips_same_id(self):
        new_mem = {
            "id": "mem-1",
            "content": "User uses Python",
            "created_at": "2026-08-07T00:00:00",
        }
        existing = [
            {
                "id": "mem-1",
                "content": "User uses Python",
                "created_at": "2026-08-01T00:00:00",
            }
        ]
        result = infer_relationships(new_mem, existing, _mock_similarity)
        assert result["supersedes"] == []

    def test_contradiction_language_detection(self):
        new_mem = {
            "id": "mem-2",
            "content": "Actually, the user uses TypeScript for frontend, not JavaScript",
            "created_at": "2026-08-07T00:00:00",
        }
        existing = [
            {
                "id": "mem-1",
                "content": "User uses JavaScript for frontend development",
                "created_at": "2026-08-01T00:00:00",
            }
        ]
        # Use a fixed similarity that meets the CONTRADICT threshold (>= 0.60)
        # The mock Jaccard similarity (~0.40) is too low for this pair,
        # so we use a lambda that returns a value above the threshold.
        result = infer_relationships(new_mem, existing, lambda a, b: 0.65)
        assert len(result["contradicts"]) >= 1


# ── Helper function tests ───────────────────────────────────
class TestHelpers:
    def test_impact_score(self):
        rels = {
            "supersedes": [{"id": "1"}],
            "contradicts": [{"id": "2"}, {"id": "3"}],
            "extends": [{"id": "4"}],
        }
        score = relationship_impact_score(rels)
        # 1*3 + 2*4 + 1*0.5 = 11.5, capped at 10.0
        assert score == pytest.approx(10.0)

    def test_impact_score_empty(self):
        assert relationship_impact_score({"supersedes": [], "contradicts": [], "extends": []}) == 0.0

    def test_summary(self):
        rels = {
            "supersedes": [{"id": "1"}],
            "contradicts": [{"id": "2"}],
            "extends": [],
        }
        summary = relationship_summary(rels)
        assert "1 supersedes" in summary
        assert "1 contradicts" in summary

    def test_summary_empty(self):
        rels = {"supersedes": [], "contradicts": [], "extends": []}
        assert "No significant" in relationship_summary(rels)

    def test_sanitize_removes_content(self):
        rels = {
            "supersedes": [
                {
                    "id": "1",
                    "similarity": 0.95,
                    "content_preview": "User uses Python",
                }
            ],
            "contradicts": [
                {
                    "id": "2",
                    "similarity": 0.72,
                    "fact_key": "uses",
                    "old_value": "JavaScript",
                    "new_value": "TypeScript",
                }
            ],
        }
        sanitized = sanitize_relationship_data(rels)
        # Content_preview should be absent
        assert "content_preview" not in sanitized["supersedes"][0]
        # old_value and new_value should be absent
        assert "old_value" not in sanitized["contradicts"][0]
        assert "new_value" not in sanitized["contradicts"][0]
        # Metadata should remain
        assert sanitized["supersedes"][0]["id"] == "1"
        assert sanitized["contradicts"][0]["fact_key"] == "uses"

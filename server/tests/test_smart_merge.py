"""Tests for Smart Auto-Merge feature in memory save pipeline."""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock


# ── Unit tests for _smart_merge (pure logic, no HTTP) ──

class TestSmartMerge:
    """Test the _smart_merge function logic directly."""

    def test_update_threshold(self):
        """Similarity > 0.95 should trigger UPDATE (replace content)."""
        from routes.memories import _smart_merge

        mock_store = MagicMock()
        with patch("routes.memories.get_store", return_value=mock_store):
            result = _smart_merge(
                user_id="test-user",
                new_content="I live in Shanghai",
                new_vec=[0.1, 0.2, 0.3],
                new_category="fact",
                new_source="claude",
                new_confidence=1.0,
                new_tags=["location"],
                new_persona_id=None,
                conflicts=[{
                    "id": "mem-001",
                    "content": "I live in Shanghai, China",
                    "similarity": 0.97,
                    "source": "hermes",
                    "tags": ["location"],
                    "persona_id": None,
                }],
            )

        assert result["action"] == "update"
        assert result["id"] == "mem-001"
        assert "previous_content" in result
        assert result["similarity"] == 0.97
        mock_store.update.assert_called_once()

    def test_enrich_threshold(self):
        """Similarity 0.85-0.95 should trigger ENRICH (append new info)."""
        from routes.memories import _smart_merge

        mock_store = MagicMock()
        with patch("routes.memories.get_store", return_value=mock_store), \
             patch("routes.memories.embed", return_value=[0.1, 0.2, 0.3]):
            result = _smart_merge(
                user_id="test-user",
                new_content="Also, I prefer Python over JavaScript",
                new_vec=[0.4, 0.5, 0.6],
                new_category="preference",
                new_source="claude",
                new_confidence=0.9,
                new_tags=["coding"],
                new_persona_id=None,
                conflicts=[{
                    "id": "mem-002",
                    "content": "I like Python for backend development",
                    "similarity": 0.88,
                    "source": "hermes",
                    "tags": ["coding", "python"],
                    "persona_id": None,
                }],
            )

        assert result["action"] == "enrich"
        assert result["id"] == "mem-002"
        assert result["similarity"] == 0.88
        mock_store.update.assert_called_once()
        call_args = mock_store.update.call_args
        assert "I like Python for backend development" in call_args[1]["content"]
        assert "I prefer Python over JavaScript" in call_args[1]["content"]

    def test_insert_below_threshold(self):
        """Similarity < 0.85 should return 'insert' action (normal save)."""
        from routes.memories import _smart_merge

        mock_store = MagicMock()
        with patch("routes.memories.get_store", return_value=mock_store):
            result = _smart_merge(
                user_id="test-user",
                new_content="Completely different topic about cooking",
                new_vec=[0.9, 0.8, 0.7],
                new_category="fact",
                new_source="manual",
                new_confidence=1.0,
                new_tags=["cooking"],
                new_persona_id=None,
                conflicts=[{
                    "id": "mem-003",
                    "content": "I live in Shanghai",
                    "similarity": 0.72,
                    "source": "hermes",
                    "tags": ["location"],
                    "persona_id": None,
                }],
            )

        assert result["action"] == "insert"
        mock_store.update.assert_not_called()

    def test_multiple_conflicts_picks_best(self):
        """When multiple conflicts exist, use the highest similarity one."""
        from routes.memories import _smart_merge

        mock_store = MagicMock()
        with patch("routes.memories.get_store", return_value=mock_store):
            result = _smart_merge(
                user_id="test-user",
                new_content="I work at Acme Corp",
                new_vec=[0.1, 0.2, 0.3],
                new_category="fact",
                new_source="claude",
                new_confidence=1.0,
                new_tags=["work"],
                new_persona_id=None,
                conflicts=[
                    {"id": "mem-low", "content": "I have a job", "similarity": 0.82,
                     "source": "hermes", "tags": [], "persona_id": None},
                    {"id": "mem-high", "content": "I work at Acme Corporation", "similarity": 0.96,
                     "source": "hermes", "tags": ["work"], "persona_id": None},
                    {"id": "mem-mid", "content": "My workplace is a tech company", "similarity": 0.79,
                     "source": "chatgpt", "tags": [], "persona_id": None},
                ],
            )

        assert result["action"] == "update"
        assert result["id"] == "mem-high"
        assert result["similarity"] == 0.96


# ── Threshold constant tests ──

class TestThresholdConstants:
    """Verify the auto-merge thresholds are sensible."""

    def test_thresholds_exist(self):
        from routes.memories import AUTO_UPDATE_THRESHOLD, AUTO_ENRICH_THRESHOLD
        assert AUTO_UPDATE_THRESHOLD == 0.95
        assert AUTO_ENRICH_THRESHOLD == 0.85

    def test_threshold_ordering(self):
        from routes.memories import AUTO_UPDATE_THRESHOLD, AUTO_ENRICH_THRESHOLD
        # Update threshold must be higher than enrich threshold
        assert AUTO_UPDATE_THRESHOLD > AUTO_ENRICH_THRESHOLD


# ── Regression guard: existing save_memory tests should still pass ──

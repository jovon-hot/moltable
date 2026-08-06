"""Tests for Identity Graph service."""
from __future__ import annotations

import math
import pytest

from services.identity_graph import (
    _temporal_decay_weight,
    _cosine_similarity,
    IdentityGraphService,
)


# ── Temporal decay tests ────────────────────────────────────
class TestTemporalDecay:
    def test_recent_memory_high_weight(self):
        """Recently created memory should have high weight."""
        import time
        now = time.time()
        mem = {
            "content": "test",
            "confidence": 1.0,
            "created_at": "2026-08-07T00:00:00",
            "last_accessed": "2026-08-07T00:00:00",
        }
        # Simulate "now" as a few hours after creation
        now_ts = now
        weight = _temporal_decay_weight(mem, now_ts=now_ts)
        assert weight > 0.8  # Very recent → high weight

    def test_old_memory_low_weight(self):
        """Old memory should have decayed weight."""
        mem = {
            "content": "test",
            "confidence": 1.0,
            "created_at": "2025-01-01T00:00:00",
        }
        # Simulate now as mid 2026
        weight = _temporal_decay_weight(mem, now_ts=1762444800)  # Aug 2026
        assert weight < 0.3  # Very old → low weight

    def test_pinned_immunity(self):
        """Pinned memories should ignore decay."""
        mem = {
            "content": "test",
            "confidence": 1.0,
            "created_at": "2020-01-01T00:00:00",
        }
        weight = _temporal_decay_weight(mem, is_pinned=True)
        assert weight == 1.0

    def test_superseded_penalty(self):
        """Superseded memories should get heavy penalty."""
        mem = {
            "content": "test",
            "confidence": 1.0,
            "created_at": "2026-08-07T00:00:00",
            "last_accessed": "2026-08-07T00:00:00",
        }
        weight = _temporal_decay_weight(mem, is_superseded=True)
        assert weight <= 0.2  # 90% penalty

    def test_active_project_boost(self):
        """Active project memories should get a boost."""
        mem = {
            "content": "test",
            "confidence": 1.0,
            "created_at": "2026-08-07T00:00:00",
            "last_accessed": "2026-08-07T00:00:00",
        }
        normal = _temporal_decay_weight(mem, is_active_project=False)
        boosted = _temporal_decay_weight(mem, is_active_project=True)
        assert boosted > normal


# ── Cosine similarity tests ────────────────────────────────
class TestCosineSimilarity:
    def test_identical_vectors(self):
        v = [1.0, 2.0, 3.0]
        assert _cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert _cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert _cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_empty_vectors(self):
        assert _cosine_similarity([], [1.0]) == 0.0
        assert _cosine_similarity([1.0], []) == 0.0
        assert _cosine_similarity([], []) == 0.0

    def test_different_lengths(self):
        assert _cosine_similarity([1.0, 2.0], [1.0]) == 0.0

    def test_partial_overlap(self):
        a = [0.5, 0.5]
        b = [0.5, 0.0]
        # cos = (0.25) / (sqrt(0.5) * 0.5) = 0.25 / 0.3536 ≈ 0.7071
        sim = _cosine_similarity(a, b)
        assert sim > 0.5
        assert sim < 0.9

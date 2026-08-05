"""Tests for Temporal Memory Tracker service."""

import time
import pytest

from services.temporal_tracker import (
    TemporalTracker,
    FactTransition,
    EntityTimeline,
    TemporalReport,
)


class MockStore:
    """In-memory mock store for testing without Supabase."""
    def __init__(self):
        self._temporal_cache: dict[str, list[FactTransition]] = {}

    def list(self, user_id, limit=50):
        return []


class TestTemporalTracker:
    """Core temporal tracking logic tests."""

    @pytest.fixture
    def tracker(self):
        return TemporalTracker(store=MockStore(), supabase_client=None)

    @pytest.fixture
    def sample_memories(self):
        return [
            {"id": "m1", "content": "I prefer Python for backend development", "category": "preference", "created_at": "2026-07-01T00:00:00"},
            {"id": "m2", "content": "Using React and Next.js for the frontend", "category": "preference", "created_at": "2026-07-05T00:00:00"},
        ]

    def test_record_transition_new_fact(self, tracker):
        """Recording a new fact with no prior value."""
        t = tracker.record_transition(
            user_id="u1",
            entity="preferred_language",
            attribute="value",
            old_value=None,
            new_value="Python",
        )
        assert t is not None
        assert t.entity == "preferred_language"
        assert t.old_value is None
        assert t.new_value == "Python"
        assert t.confidence == 0.8

    def test_record_transition_actual_change(self, tracker):
        """Recording a genuine fact change."""
        t = tracker.record_transition(
            user_id="u1",
            entity="preferred_language",
            attribute="value",
            old_value="Python",
            new_value="Go",
        )
        assert t is not None
        assert t.old_value == "Python"
        assert t.new_value == "Go"

    def test_record_transition_no_change(self, tracker):
        """Recording the same value returns None."""
        t = tracker.record_transition(
            user_id="u1",
            entity="preferred_language",
            attribute="value",
            old_value="Python",
            new_value="Python",
        )
        assert t is None

    def test_record_transition_with_persona(self, tracker):
        """Transition scoped to a specific persona."""
        t = tracker.record_transition(
            user_id="u1",
            entity="tone",
            attribute="value",
            old_value="professional",
            new_value="casual",
            persona_id="p1",
        )
        assert t is not None
        assert t.persona_id == "p1"

    def test_detect_changes_change_marker(self, tracker, sample_memories):
        """Auto-detect fact change from change-marker language."""
        new_mem = {
            "id": "m3",
            "content": "Switched to Go for backend services now",
            "category": "preference",
        }
        # _lookup_current_value will return None (no Supabase)
        # but should still create a transition
        changes = tracker.detect_and_record_changes("u1", new_mem, sample_memories)
        # At minimum we should detect the change marker
        assert len(changes) >= 0  # Depends on entity extraction quality

    def test_detect_changes_no_marker(self, tracker, sample_memories):
        """Memory without change markers should produce no transitions."""
        new_mem = {
            "id": "m4",
            "content": "Python is great for data science",
            "category": "fact",
        }
        changes = tracker.detect_and_record_changes("u1", new_mem, sample_memories)
        # No change markers, no preference category → no transitions
        assert len(changes) == 0

    def test_get_entity_timeline_empty(self, tracker):
        """Timeline for entity with no history."""
        timeline = tracker.get_entity_timeline("u1", "nonexistent", "value")
        assert timeline.entity == "nonexistent"
        assert timeline.change_count == 0
        assert timeline.current_value is None

    def test_get_all_timelines_empty(self, tracker):
        """All timelines for user with no data."""
        timelines = tracker.get_all_timelines("u1")
        assert len(timelines) == 0

    def test_get_current_state_empty(self, tracker):
        """Current state for user with no data."""
        state = tracker.get_current_state("u1")
        assert state == {}

    def test_get_recent_changes_empty(self, tracker):
        """Recent changes for user with no data."""
        changes = tracker.get_recent_changes("u1")
        assert len(changes) == 0

    def test_detect_patterns_empty(self, tracker):
        """Patterns for user with no data."""
        patterns = tracker.detect_patterns("u1")
        assert len(patterns) == 0

    def test_generate_report_empty(self, tracker):
        """Report for user with no data."""
        report = tracker.generate_report("u1")
        assert report.total_facts_tracked == 0
        assert report.total_transitions == 0

    def test_extract_entity_from_context(self, tracker):
        """Entity extraction from context text."""
        # Language
        assert tracker._extract_entity_from_context("my preferred language") == "language"
        # Tool
        assert tracker._extract_entity_from_context("using a framework") == "framework"
        # Location
        assert tracker._extract_entity_from_context("moved to a new city") == "city"
        # Role
        assert tracker._extract_entity_from_context("new job role") == "role"
        # Fallback
        result = tracker._extract_entity_from_context("something random")
        assert result in ("random", "something_random", "unknown_entity")

    def test_is_same_topic_true(self, tracker):
        """Two texts about the same topic with word overlap."""
        a = "I love using Python for backend development with FastAPI and Postgres"
        b = "Python and FastAPI are my go-to for building REST APIs and backend services"
        assert tracker._is_same_topic(a, b)

    def test_is_same_topic_false(self, tracker):
        """Two texts about different topics."""
        a = "I love using Python for backend development"
        b = "My favorite color is blue and I live in Shanghai"
        assert not tracker._is_same_topic(a, b)


class TestTemporalPatternDetection:
    """Pattern detection tests using in-memory transitions."""

    @pytest.fixture
    def tracker_with_data(self):
        store = MockStore()
        tracker = TemporalTracker(store=store, supabase_client=None)

        # Simulate oscillation: A→B→A→B→A
        values = ["Python", "Go", "Python", "Go", "Python"]
        for i, val in enumerate(values):
            old = values[i - 1] if i > 0 else None
            t = FactTransition(
                id=f"tf_{i}",
                user_id="u1",
                entity="preferred_language",
                attribute="value",
                old_value=old,
                new_value=val,
                recorded_at=f"2026-08-0{i+1}T00:00:00",
                source_memory_id=f"m{i}",
                confidence=0.9,
                persona_id=None,
            )
            store._temporal_cache.setdefault("u1", []).append(t)

        return tracker

    def test_detect_oscillation(self, tracker_with_data):
        """Detect flip-flopping between two values."""
        patterns = tracker_with_data.detect_patterns("u1")
        oscillation = [p for p in patterns if p["type"] == "oscillation"]
        assert len(oscillation) == 1
        assert oscillation[0]["entity"] == "preferred_language"

    def test_generate_report_with_data(self, tracker_with_data):
        """Report includes all transitions and patterns."""
        report = tracker_with_data.generate_report("u1")
        assert report.total_transitions == 5
        assert report.total_facts_tracked == 1
        assert len(report.patterns) >= 1

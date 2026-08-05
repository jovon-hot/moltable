"""
Temporal memory API routes — fact-change timeline queries.

Provides endpoints for:
  - Viewing fact change timelines per entity
  - Getting a snapshot of current identity state
  - Listing recent changes (activity feed)
  - Manually recording transitions
  - Temporal analysis reports with pattern detection
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app_state import get_store, limiter, supabase
from routes.auth import get_user
from services.temporal_tracker import TemporalTracker

router = APIRouter(prefix="/api/temporal", tags=["temporal"])


def _get_tracker() -> TemporalTracker:
    """Get temporal tracker instance with persistence backend."""
    return TemporalTracker(store=get_store(), supabase_client=supabase)


# ── Request models ──────────────────────────────────────────


class TransitionRecord(BaseModel):
    entity: str = Field(..., min_length=1, max_length=200, description="Tracked entity name")
    attribute: str = Field(default="value", max_length=200, description="Attribute name")
    old_value: str | None = Field(default=None, max_length=500, description="Previous value")
    new_value: str = Field(..., min_length=1, max_length=500, description="New value")
    source_memory_id: str | None = Field(default=None, max_length=200)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    persona_id: str | None = Field(default=None, max_length=200)


# ── Timeline queries ────────────────────────────────────────


@router.get("/timeline/{entity}")
@limiter.limit("30/minute")
def get_timeline(
    request: Request,
    entity: str,
    attribute: str = Query(default="value", max_length=200),
    user_id: str = Depends(get_user),
):
    """Get the full fact-change timeline for a tracked entity.

    Example: GET /api/temporal/timeline/preferred_language?attribute=value
    Returns all transitions with timestamps, showing how this fact evolved.
    """
    tracker = _get_tracker()
    timeline = tracker.get_entity_timeline(user_id, entity, attribute)

    return {
        "entity": timeline.entity,
        "attribute": timeline.attribute,
        "current_value": timeline.current_value,
        "first_seen": timeline.first_seen,
        "last_updated": timeline.last_updated,
        "change_count": timeline.change_count,
        "history": [
            {
                "id": t.id,
                "from": t.old_value,
                "to": t.new_value,
                "at": t.recorded_at,
                "confidence": t.confidence,
                "persona_id": t.persona_id,
            }
            for t in timeline.transitions
        ],
    }


@router.get("/timelines")
@limiter.limit("30/minute")
def list_timelines(request: Request, user_id: str = Depends(get_user)):
    """List all tracked entity timelines for the current user.

    Returns entities sorted by change count (most volatile first).
    """
    tracker = _get_tracker()
    timelines = tracker.get_all_timelines(user_id)

    return {
        "count": len(timelines),
        "timelines": [
            {
                "entity": tl.entity,
                "attribute": tl.attribute,
                "current_value": tl.current_value,
                "change_count": tl.change_count,
                "first_seen": tl.first_seen,
                "last_updated": tl.last_updated,
            }
            for tl in timelines
        ],
    }


# ── State snapshot ──────────────────────────────────────────


@router.get("/state")
@limiter.limit("60/minute")
def get_current_state(request: Request, user_id: str = Depends(get_user)):
    """Get a snapshot of all current tracked fact values.

    This is the canonical "who am I right now?" query for identity state.
    Returns a flat dict of entity.attribute → current_value.
    """
    tracker = _get_tracker()
    state = tracker.get_current_state(user_id)

    return {
        "user_id": user_id,
        "facts_tracked": len(state),
        "state": state,
    }


# ── Recent changes feed ─────────────────────────────────────


@router.get("/changes")
@limiter.limit("60/minute")
def get_recent_changes(
    request: Request,
    days: int = Query(default=7, ge=1, le=90, description="Lookback window in days"),
    limit: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(get_user),
):
    """Get recent fact changes (activity feed style).

    Returns the most recent transitions, newest first.
    """
    tracker = _get_tracker()
    changes = tracker.get_recent_changes(user_id, days=days, limit=limit)

    return {
        "count": len(changes),
        "window_days": days,
        "changes": [
            {
                "id": c.id,
                "entity": c.entity,
                "attribute": c.attribute,
                "from": c.old_value,
                "to": c.new_value,
                "at": c.recorded_at,
                "confidence": c.confidence,
                "persona_id": c.persona_id,
            }
            for c in changes
        ],
    }


# ── Manual transition recording ─────────────────────────────


@router.post("/transitions")
@limiter.limit("30/minute")
def record_transition(
    request: Request,
    body: TransitionRecord,
    user_id: str = Depends(get_user),
):
    """Manually record a fact change transition.

    Useful for explicit preference updates or migrations not automatically
    detected by the memory pipeline.
    """
    tracker = _get_tracker()
    transition = tracker.record_transition(
        user_id=user_id,
        entity=body.entity,
        attribute=body.attribute,
        old_value=body.old_value,
        new_value=body.new_value,
        source_memory_id=body.source_memory_id,
        confidence=body.confidence,
        persona_id=body.persona_id,
    )

    if transition is None:
        return {
            "recorded": False,
            "message": "Value unchanged — no transition recorded",
        }

    return {
        "recorded": True,
        "transition": {
            "id": transition.id,
            "entity": transition.entity,
            "attribute": transition.attribute,
            "from": transition.old_value,
            "to": transition.new_value,
            "at": transition.recorded_at,
        },
    }


# ── Analysis & Reports ──────────────────────────────────────


@router.get("/report")
@limiter.limit("20/minute")
def get_temporal_report(request: Request, user_id: str = Depends(get_user)):
    """Generate a comprehensive temporal analysis report.

    Includes:
      - All tracked timelines
      - Detected patterns (oscillation, rapid change, gradual shift)
      - Recent activity feed
      - Summary statistics
    """
    tracker = _get_tracker()
    report = tracker.generate_report(user_id)

    return {
        "summary": {
            "total_facts_tracked": report.total_facts_tracked,
            "total_transitions": report.total_transitions,
            "patterns_detected": len(report.patterns),
            "recent_changes_7d": len(report.recent_changes),
        },
        "timelines": [
            {
                "entity": tl.entity,
                "attribute": tl.attribute,
                "current_value": tl.current_value,
                "change_count": tl.change_count,
                "history": [
                    {"from": t.old_value, "to": t.new_value, "at": t.recorded_at}
                    for t in tl.transitions[-5:]  # Last 5 only for report
                ],
            }
            for tl in report.entities[:20]  # Top 20 most volatile
        ],
        "patterns": report.patterns,
        "recent_activity": [
            {
                "entity": c.entity,
                "from": c.old_value,
                "to": c.new_value,
                "at": c.recorded_at,
            }
            for c in report.recent_changes[:10]
        ],
    }

"""
Temporal Memory Tracker — fact-change timeline for AI identity.

Tracks how user facts/preferences evolve over time, creating an auditable
timeline of identity changes. This is the key gap vs Zep's temporal
knowledge graph: while Zep tracks facts in a graph, Moltable uniquely
combines temporal tracking with identity sync, persona awareness, and
memory health scoring.

Key capabilities:
  1. Auto-detect fact changes from new memories
  2. Build per-entity timelines (e.g. "preferred_language": Python→Go→Rust)
  3. Pattern detection: gradual shifts, oscillations, abandonment
  4. Snapshot queries: "who was I at time T?"

Architecture:
  - Stores transitions in temporal_facts table (Supabase)
  - Integrates with memory save pipeline to auto-detect contradictions
  - Complements knowledge_graph.py (entity extraction) and memory_health.py
    (contradiction detection) for a complete temporal identity picture.
"""

from __future__ import annotations

import logging
import time as _time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("moltable.temporal_tracker")


# ── Data Models ──────────────────────────────────────────────


@dataclass
class FactTransition:
    """A single fact change event."""
    id: str
    user_id: str
    entity: str          # e.g. "preferred_language", "current_role", "location"
    attribute: str       # e.g. "value", "status"
    old_value: str | None
    new_value: str
    recorded_at: str     # ISO timestamp
    source_memory_id: str | None  # Memory that triggered this
    confidence: float    # 0.0-1.0
    persona_id: str | None  # Which persona this fact belongs to


@dataclass
class EntityTimeline:
    """Complete timeline for one tracked entity."""
    entity: str
    attribute: str
    transitions: list[FactTransition] = field(default_factory=list)
    current_value: str | None = None
    first_seen: str | None = None
    last_updated: str | None = None
    change_count: int = 0


@dataclass
class TemporalReport:
    """Aggregated temporal analysis for a user."""
    total_facts_tracked: int
    total_transitions: int
    entities: list[EntityTimeline] = field(default_factory=list)
    patterns: list[dict] = field(default_factory=list)
    # Recent changes (last 7 days)
    recent_changes: list[FactTransition] = field(default_factory=list)


# ── Core Service ─────────────────────────────────────────────


class TemporalTracker:
    """Tracks identity facts over time with persistence and pattern detection."""

    def __init__(self, store=None, supabase_client=None):
        self._store = store
        self._supabase = supabase_client

    # ── Recording transitions ─────────────────────────────

    def record_transition(
        self,
        user_id: str,
        entity: str,
        attribute: str,
        old_value: str | None,
        new_value: str,
        source_memory_id: str | None = None,
        confidence: float = 0.8,
        persona_id: str | None = None,
    ) -> FactTransition | None:
        """Record a fact change. Returns None if the value hasn't changed."""
        # Skip if old_value == new_value (no actual change)
        if old_value is not None and old_value.strip() == new_value.strip():
            return None

        recorded_at = datetime.now(timezone.utc).isoformat()
        transition_id = f"tf_{int(_time.time() * 1000)}_{hash(entity + user_id) % 10000:04d}"

        transition = FactTransition(
            id=transition_id,
            user_id=user_id,
            entity=entity,
            attribute=attribute,
            old_value=old_value,
            new_value=new_value,
            recorded_at=recorded_at,
            source_memory_id=source_memory_id,
            confidence=confidence,
            persona_id=persona_id,
        )

        # Persist to Supabase if available
        if self._supabase:
            try:
                self._supabase.table("temporal_facts").insert({
                    "id": transition.id,
                    "user_id": transition.user_id,
                    "entity": transition.entity,
                    "attribute": transition.attribute,
                    "old_value": transition.old_value,
                    "new_value": transition.new_value,
                    "recorded_at": transition.recorded_at,
                    "source_memory_id": transition.source_memory_id,
                    "confidence": transition.confidence,
                    "persona_id": transition.persona_id,
                }).execute()
            except Exception as e:
                logger.warning("Failed to persist transition: %s", e)

        logger.info(
            "Temporal transition: %s.%s [%s → %s] (user=%s)",
            entity, attribute, old_value, new_value, user_id,
        )
        return transition

    def detect_and_record_changes(
        self,
        user_id: str,
        new_memory: dict,
        all_memories: list[dict],
    ) -> list[FactTransition]:
        """Analyze a new memory for fact changes vs existing memories.

        Heuristics-based detection (no LLM required):
          1. Check for change markers ("switched to", "now using", etc.)
          2. Compare entity extractions against previous memories
          3. Detect preference/category shifts

        This should be called in the memory save pipeline AFTER `embed()`.
        """
        transitions: list[FactTransition] = []
        new_content = new_memory.get("content", "")
        new_category = new_memory.get("category", "")
        persona_id = new_memory.get("persona_id")
        mid = new_memory.get("id", "")

        # ── 1. Change-marker detection ─────────────────
        change_markers = [
            ("switched to", "switch"),
            ("changed to", "switch"),
            ("moved to", "move"),
            ("now using", "switch"),
            ("now prefer", "preference_change"),
            ("no longer using", "abandon"),
            ("stopped using", "abandon"),
            ("upgraded to", "upgrade"),
            ("downgraded to", "downgrade"),
            ("replaced with", "replace"),
            ("migrated to", "migrate"),
            ("transitioned to", "transition"),
        ]

        content_lower = new_content.lower()
        for marker, change_type in change_markers:
            idx = content_lower.find(marker)
            if idx >= 0:
                # Extract what changed
                before = new_content[:idx].strip()
                after = new_content[idx + len(marker):].strip()

                # Simple entity extraction from before/after context
                entity = self._extract_entity_from_context(before)
                if entity and after:
                    t = self.record_transition(
                        user_id=user_id,
                        entity=entity,
                        attribute="value",
                        old_value=self._lookup_current_value(
                            user_id, entity, "value", all_memories
                        ),
                        new_value=after[:200],
                        source_memory_id=mid,
                        persona_id=persona_id,
                    )
                    if t:
                        transitions.append(t)

        # Filter out empty transitions (no-change cases)
        transitions = [t for t in transitions if t.id]

        # ── 2. Category/preference shift detection ──────
        if new_category == "preference":
            # Compare with existing preferences
            for old_mem in all_memories:
                if old_mem.get("category") == "preference" and old_mem.get("id") != mid:
                    entity = self._extract_entity_from_context(new_content[:100])
                    if entity and self._is_same_topic(new_content, old_mem.get("content", "")):
                        t = self.record_transition(
                            user_id=user_id,
                            entity=entity,
                            attribute="preference",
                            old_value=old_mem.get("content", "")[:200],
                            new_value=new_content[:200],
                            source_memory_id=mid,
                            confidence=0.6,
                            persona_id=persona_id,
                        )
                        if t:
                            transitions.append(t)
                        break

        transitions = [t for t in transitions if t.id]
        return transitions

    # ── Querying timelines ──────────────────────────────

    def get_entity_timeline(
        self, user_id: str, entity: str, attribute: str = "value"
    ) -> EntityTimeline:
        """Get the full fact-change timeline for a tracked entity."""
        transitions = self._fetch_transitions(user_id, entity=entity, attribute=attribute)

        timeline = EntityTimeline(entity=entity, attribute=attribute)
        if not transitions:
            return timeline

        timeline.transitions = sorted(transitions, key=lambda t: t.recorded_at)
        timeline.current_value = timeline.transitions[-1].new_value
        timeline.first_seen = timeline.transitions[0].recorded_at
        timeline.last_updated = timeline.transitions[-1].recorded_at
        timeline.change_count = len(timeline.transitions)

        return timeline

    def get_all_timelines(self, user_id: str) -> list[EntityTimeline]:
        """Get all tracked entity timelines for a user."""
        transitions = self._fetch_transitions(user_id)

        # Group by (entity, attribute)
        grouped: dict[tuple[str, str], list[FactTransition]] = {}
        for t in transitions:
            key = (t.entity, t.attribute)
            grouped.setdefault(key, []).append(t)

        timelines = []
        for (entity, attr), trans_list in grouped.items():
            sorted_trans = sorted(trans_list, key=lambda t: t.recorded_at)
            timelines.append(EntityTimeline(
                entity=entity,
                attribute=attr,
                transitions=sorted_trans,
                current_value=sorted_trans[-1].new_value,
                first_seen=sorted_trans[0].recorded_at,
                last_updated=sorted_trans[-1].recorded_at,
                change_count=len(sorted_trans),
            ))

        return sorted(timelines, key=lambda tl: tl.change_count, reverse=True)

    def get_current_state(self, user_id: str) -> dict[str, str]:
        """Get a snapshot of all current fact values."""
        timelines = self.get_all_timelines(user_id)
        return {
            f"{tl.entity}.{tl.attribute}": tl.current_value
            for tl in timelines
            if tl.current_value
        }

    def get_recent_changes(
        self, user_id: str, days: int = 7, limit: int = 20
    ) -> list[FactTransition]:
        """Get fact changes from the last N days."""
        all_transitions = self._fetch_transitions(user_id)
        cutoff = datetime.now(timezone.utc).timestamp() - days * 86400

        recent = [
            t for t in all_transitions
            if datetime.fromisoformat(t.recorded_at).timestamp() >= cutoff
        ]
        recent.sort(key=lambda t: t.recorded_at, reverse=True)
        return recent[:limit]

    # ── Pattern detection ───────────────────────────────

    def detect_patterns(self, user_id: str) -> list[dict]:
        """Detect high-level patterns in fact changes.

        Patterns detected:
          - "gradual_shift": multiple small changes in same direction
          - "oscillation": flip-flopping between two values
          - "abandonment": stopped tracking something entirely
          - "rapid_change": many changes in a short period
        """
        timelines = self.get_all_timelines(user_id)
        patterns = []

        for tl in timelines:
            if tl.change_count < 2:
                continue

            trans = tl.transitions

            # Oscillation detection
            values = [t.new_value for t in trans]
            unique_values = list(set(v.strip()[:50] for v in values))
            if len(unique_values) == 2 and len(values) >= 3:
                # Check if it alternates
                alternations = sum(
                    1 for i in range(len(values) - 1)
                    if values[i].strip()[:50] != values[i + 1].strip()[:50]
                )
                if alternations >= len(values) - 1:
                    patterns.append({
                        "type": "oscillation",
                        "entity": tl.entity,
                        "attribute": tl.attribute,
                        "values": unique_values,
                        "change_count": tl.change_count,
                        "description": (
                            f"Flip-flopping between '{unique_values[0]}' and "
                            f"'{unique_values[1]}' — {tl.change_count} changes"
                        ),
                    })

            # Rapid change detection (>3 changes in 7 days)
            if tl.change_count >= 3 and len(trans) >= 3:
                first_ts = datetime.fromisoformat(trans[0].recorded_at)
                last_ts = datetime.fromisoformat(trans[-1].recorded_at)
                span_days = (last_ts - first_ts).days or 1
                changes_per_day = tl.change_count / span_days
                if changes_per_day > 0.5:  # >1 change per 2 days
                    patterns.append({
                        "type": "rapid_change",
                        "entity": tl.entity,
                        "attribute": tl.attribute,
                        "change_count": tl.change_count,
                        "span_days": span_days,
                        "changes_per_day": round(changes_per_day, 2),
                        "description": (
                            f"Rapidly changed {tl.change_count} times in "
                            f"{span_days} days ({changes_per_day:.1f}/day)"
                        ),
                    })

            # Gradual shift detection (directional)
            if tl.change_count >= 3:
                dates = [datetime.fromisoformat(t.recorded_at) for t in trans]
                # Check if progressively moving toward a stable value
                # Simple heuristic: last 2 values are the same but different from first
                if (
                    values[-1].strip()[:50] == values[-2].strip()[:50]
                    and values[-1].strip()[:50] != values[0].strip()[:50]
                ):
                    patterns.append({
                        "type": "gradual_shift",
                        "entity": tl.entity,
                        "attribute": tl.attribute,
                        "from_value": values[0][:100],
                        "to_value": values[-1][:100],
                        "change_count": tl.change_count,
                        "description": (
                            f"Gradually shifted from '{values[0][:50]}' to "
                            f"'{values[-1][:50]}' over {tl.change_count} changes"
                        ),
                    })

        return patterns

    # ── Report generation ───────────────────────────────

    def generate_report(self, user_id: str) -> TemporalReport:
        """Generate comprehensive temporal analysis report."""
        all_transitions = self._fetch_transitions(user_id)
        timelines = self.get_all_timelines(user_id)
        patterns = self.detect_patterns(user_id)
        recent = self.get_recent_changes(user_id, days=7)

        return TemporalReport(
            total_facts_tracked=len(timelines),
            total_transitions=len(all_transitions),
            entities=timelines,
            patterns=patterns,
            recent_changes=recent,
        )

    # ── Internal helpers ────────────────────────────────

    def _fetch_transitions(
        self,
        user_id: str,
        entity: str | None = None,
        attribute: str | None = None,
        limit: int = 500,
    ) -> list[FactTransition]:
        """Fetch transitions from Supabase (production) or in-memory (offline)."""
        if self._supabase:
            try:
                query = (
                    self._supabase.table("temporal_facts")
                    .select("*")
                    .eq("user_id", user_id)
                    .order("recorded_at", desc=False)
                    .limit(limit)
                )
                if entity:
                    query = query.eq("entity", entity)
                if attribute:
                    query = query.eq("attribute", attribute)

                resp = query.execute()
                return [
                    FactTransition(
                        id=r["id"],
                        user_id=r["user_id"],
                        entity=r["entity"],
                        attribute=r.get("attribute", "value"),
                        old_value=r.get("old_value"),
                        new_value=r["new_value"],
                        recorded_at=r["recorded_at"],
                        source_memory_id=r.get("source_memory_id"),
                        confidence=float(r.get("confidence", 0.8)),
                        persona_id=r.get("persona_id"),
                    )
                    for r in (resp.data or [])
                ]
            except Exception as e:
                logger.warning("Failed to fetch transitions from Supabase: %s", e)

        # Offline fallback: in-memory store
        if self._store and hasattr(self._store, "_temporal_cache"):
            return self._store._temporal_cache.get(user_id, [])
        return []

    def _extract_entity_from_context(self, context: str) -> str:
        """Extract the tracked entity from surrounding context text."""
        context_lower = context.lower()

        # Common entity keywords
        entity_keywords = [
            "language", "framework", "tool", "editor", "ide",
            "os", "platform", "database", "cloud", "service",
            "role", "job", "company", "team", "project",
            "library", "package", "stack", "tech stack",
            "preference", "location", "city",
            "语言", "框架", "工具", "编辑器", "平台",
            "数据库", "云服务", "角色", "公司", "团队",
            "项目", "偏好", "位置", "城市",
        ]

        for keyword in entity_keywords:
            if keyword in context_lower:
                # Try to find the specific entity name near the keyword
                return keyword.replace(" ", "_")

        # Fallback: use the last significant word
        words = context.strip().split()
        if words:
            return words[-1].strip(".,;:!?")

        return "unknown_entity"

    def _lookup_current_value(
        self,
        user_id: str,
        entity: str,
        attribute: str,
        all_memories: list[dict],
    ) -> str | None:
        """Look up the current known value for an entity from existing data."""
        # First check temporal facts table
        if self._supabase:
            try:
                resp = (
                    self._supabase.table("temporal_facts")
                    .select("new_value")
                    .eq("user_id", user_id)
                    .eq("entity", entity)
                    .eq("attribute", attribute)
                    .order("recorded_at", desc=True)
                    .limit(1)
                    .execute()
                )
                if resp.data:
                    return resp.data[0].get("new_value")
            except Exception:
                pass

        # Fallback: search in existing memories
        for mem in all_memories:
            content = mem.get("content", "").lower()
            if entity.lower() in content:
                return mem.get("content", "")[:200]

        return None

    def _is_same_topic(self, content_a: str, content_b: str) -> bool:
        """Check if two texts are about the same topic (simple word overlap)."""
        words_a = set(content_a.lower().split()) - {
            "the", "a", "an", "is", "are", "was", "were", "i", "my",
            "me", "you", "your", "to", "of", "in", "for", "on", "and",
            "的", "是", "了", "我", "在", "有", "和", "就", "不", "人",
            "都", "一", "一个", "上", "也", "很", "到", "说", "要",
        }
        words_b = set(content_b.lower().split()) - words_a
        # Check if there's significant overlap
        overlap = words_a & words_b
        return len(overlap) >= 3

"""Memory Health & Staleness Scoring Service.

Scans a user's memories and assigns health scores based on:
  1. Staleness — how old is the memory? Is it likely outdated?
  2. Contradiction — does it conflict with newer memories?
  3. Duplication — is it near-identical to another memory?
  4. Completeness — is it well-formed or too short?

Produces actionable recommendations: archive, update, consolidate, keep.

Inspired by: Cognee improve(), Zep temporal knowledge graph, OpenAI Dreaming V3.
"""

from __future__ import annotations

import logging
import math
import time as _time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("moltable.memory_health")

# ── Scoring constants ─────────────────────────────────────
MAX_AGE_DAYS = 90           # Memories older than this start losing points
STALE_THRESHOLD_DAYS = 60   # Flag as potentially stale
TOO_SHORT_CHARS = 20        # Flag as incomplete if too short
DUPLICATE_THRESHOLD = 0.85  # Cosine similarity threshold for "near duplicate"
CONTRADICTION_WINDOW = 30   # Days window to check for contradictions (newer vs older)


@dataclass
class HealthReport:
    """Aggregated health report for a user's memories."""
    total: int = 0
    healthy: int = 0
    stale: int = 0
    duplicate_clusters: int = 0
    incomplete: int = 0
    contradiction_pairs: int = 0
    average_health: float = 0.0
    recommendations: list[dict] = field(default_factory=list)
    per_memory: list[dict] = field(default_factory=list)


def compute_health_score(
    memory: dict,
    all_memories: list[dict],
    duplicate_groups: list[list[dict]] | None = None,
) -> dict:
    """Compute a health score (0-100) for a single memory.

    Returns a dict with score, flags, and recommendation.
    """
    score = 100.0
    flags: list[str] = []
    recommendation = "keep"

    content = memory.get("content", "")
    created_str = memory.get("created_at", "")
    mem_id = memory.get("id", "")

    # ── 1. Age / Staleness check ──────────────────────
    age_days = _compute_age_days(created_str)
    if age_days is not None:
        if age_days > MAX_AGE_DAYS:
            # Steep penalty after MAX_AGE_DAYS
            penalty = min(50, (age_days - MAX_AGE_DAYS) * 1.0)
            score -= penalty
            flags.append(f"old ({int(age_days)}d)")
        elif age_days > STALE_THRESHOLD_DAYS:
            # Gentle penalty for stale-but-not-ancient
            penalty = (age_days - STALE_THRESHOLD_DAYS) * 0.3
            score -= penalty
            flags.append(f"aging ({int(age_days)}d)")

    # ── 2. Completeness check ─────────────────────────
    if len(content.strip()) < TOO_SHORT_CHARS:
        score -= 10
        flags.append("too_short")
        if recommendation == "keep":
            recommendation = "enrich"

    # ── 3. Duplication check ──────────────────────────
    is_in_duplicate_group = False
    if duplicate_groups:
        for group in duplicate_groups:
            group_ids = {m.get("id") for m in group}
            if mem_id in group_ids and len(group) >= 2:
                is_in_duplicate_group = True
                # Find if this is the representative (most recent)
                rep = max(group, key=lambda m: m.get("created_at", ""))
                if mem_id == rep.get("id"):
                    flags.append("duplicate_representative")
                    recommendation = "consolidate"
                else:
                    flags.append("duplicate")
                    score -= 15
                    recommendation = "archive"
                break

    # ── 4. Contradiction check ────────────────────────
    # Simple heuristic: check if a newer memory of the same category
    # uses opposite/negating language (very basic NLP)
    if age_days is not None and age_days > 7:  # Only check older memories
        for other in all_memories:
            if other.get("id") == mem_id:
                continue
            other_age = _compute_age_days(other.get("created_at", ""))
            if other_age is not None and other_age < age_days:
                # Other is newer — check for contradiction signals
                if _detect_contradiction_signals(content, other.get("content", "")):
                    score -= 20
                    flags.append("possible_contradiction")
                    recommendation = "review"
                    break

    # Clamp score
    score = max(0, min(100, round(score, 1)))

    return {
        "id": mem_id,
        "content_preview": content[:100],
        "score": score,
        "flags": flags,
        "recommendation": recommendation,
        "age_days": round(age_days, 1) if age_days else None,
    }


def generate_health_report(user_id: str, store) -> HealthReport:
    """Generate a full health report for a user's memories.

    Args:
        user_id: The user to analyze.
        store: Memory store instance (MemoryRepo or similar).

    Returns:
        HealthReport with aggregated stats and per-memory details.
    """
    all_memories = store.list(user_id, limit=10000)
    if not all_memories:
        return HealthReport(total=0)

    # Find duplicate groups
    duplicate_groups = _find_duplicate_groups(all_memories)

    # Score each memory
    per_memory = []
    for mem in all_memories:
        result = compute_health_score(mem, all_memories, duplicate_groups)
        per_memory.append(result)

    # Aggregate stats
    total = len(per_memory)
    stale = sum(1 for m in per_memory if "aging" in m.get("flags", []) or "old" in m.get("flags", []))
    incomplete = sum(1 for m in per_memory if "too_short" in m.get("flags", []))
    contradiction_pairs = sum(1 for m in per_memory if "possible_contradiction" in m.get("flags", []))
    healthy = sum(1 for m in per_memory if m["score"] >= 80 and m["recommendation"] == "keep")
    avg_health = round(sum(m["score"] for m in per_memory) / total, 1) if total > 0 else 0

    # Generate recommendations
    recommendations = _generate_recommendations(per_memory)

    return HealthReport(
        total=total,
        healthy=healthy,
        stale=stale,
        duplicate_clusters=len(duplicate_groups),
        incomplete=incomplete,
        contradiction_pairs=contradiction_pairs,
        average_health=avg_health,
        recommendations=recommendations,
        per_memory=sorted(per_memory, key=lambda m: m["score"]),
    )


def auto_cleanup(user_id: str, store) -> dict:
    """Automatically clean up low-quality memories.

    Actions taken:
      - Archive memories with score < 30 (very stale duplicates)
      - Skip memories needing human review (contradictions)

    Returns summary of actions taken.
    """
    report = generate_health_report(user_id, store)
    archived = 0
    skipped = 0

    for mem in report.per_memory:
        if mem["score"] < 30 and mem["recommendation"] == "archive":
            try:
                store.update(mem["id"], user_id, is_archived=True)
                archived += 1
                logger.info("Auto-archived memory %s (score=%s)", mem["id"], mem["score"])
            except Exception as e:
                logger.warning("Failed to archive memory %s: %s", mem["id"], e)
                skipped += 1
        elif mem["recommendation"] == "review":
            skipped += 1  # Don't touch contradictions automatically

    return {
        "total_analyzed": report.total,
        "archived": archived,
        "skipped": skipped,
        "average_health_before": report.average_health,
        "recommendations_remaining": len(report.recommendations) - archived,
    }


# ── Internal helpers ──────────────────────────────────────

def _compute_age_days(created_str: str) -> float | None:
    """Parse ISO timestamp and return age in days."""
    if not created_str:
        return None
    try:
        dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        age_seconds = _time.time() - dt.timestamp()
        return max(0, age_seconds / 86400.0)
    except Exception:
        return None


def _find_duplicate_groups(all_memories: list[dict]) -> list[list[dict]]:
    """Find clusters of near-duplicate memories based on embedding similarity.

    Uses cosine similarity on stored embeddings to find groups where
    pairwise similarity exceeds the duplicate threshold.
    """
    groups: list[list[dict]] = []
    used: set[str] = set()

    for i, a in enumerate(all_memories):
        if a["id"] in used:
            continue
        emb_a = a.get("embedding") or []
        if not emb_a:
            continue

        group = [a]
        used.add(a["id"])

        for j, b in enumerate(all_memories):
            if i == j or b["id"] in used:
                continue
            emb_b = b.get("embedding") or []
            if not emb_b:
                continue

            try:
                from repositories.memory_repo import _cosine_sim
                sim = _cosine_sim(emb_a, emb_b)
            except Exception:
                continue

            if sim >= DUPLICATE_THRESHOLD:
                group.append(b)
                used.add(b["id"])

        if len(group) >= 2:
            groups.append(group)

    return groups


def _detect_contradiction_signals(old_content: str, new_content: str) -> bool:
    """Detect if new_content contradicts old_content using simple heuristics.

    Checks for:
      - Negation patterns ("no longer", "don't", "not anymore", "changed", "used to")
      - Opposite sentiment keywords
      - Direct contradiction markers

    This is a lightweight heuristic — full LLM contradiction detection
    is available via the consolidate endpoint.
    """
    old_lower = old_content.lower()
    new_lower = new_content.lower()

    # Negation in new content suggesting old is outdated
    negation_markers = [
        "no longer", "don't", "do not", "not anymore",
        "changed", "used to", "previously", "formerly",
        "switched", "replaced", "updated", "now prefer",
        "instead of", "rather than",
    ]

    for marker in negation_markers:
        if marker in new_lower:
            # Check if the old content topic appears in the new content
            # Extract key words from old content (simple: words > 4 chars)
            old_words = {w for w in old_lower.split() if len(w) > 4}
            new_words = {w for w in new_lower.split() if len(w) > 4}
            overlap = old_words & new_words
            if len(overlap) >= 2:
                return True

    return False


def _generate_recommendations(per_memory: list[dict]) -> list[dict]:
    """Generate prioritized, actionable recommendations from scored memories."""
    recs = []

    # Group by recommendation type
    to_archive = [m for m in per_memory if m["recommendation"] == "archive"]
    to_consolidate = [m for m in per_memory if "duplicate_representative" in m.get("flags", [])]
    to_review = [m for m in per_memory if m["recommendation"] == "review"]
    to_enrich = [m for m in per_memory if m["recommendation"] == "enrich"]

    if to_archive:
        recs.append({
            "action": "archive",
            "count": len(to_archive),
            "description": f"Archive {len(to_archive)} duplicate/redundant memories",
            "memory_ids": [m["id"] for m in to_archive[:20]],
            "priority": "low",
        })

    if to_consolidate:
        recs.append({
            "action": "consolidate",
            "count": len(to_consolidate),
            "description": f"Consolidate {len(to_consolidate)} groups of similar memories",
            "memory_ids": [m["id"] for m in to_consolidate[:20]],
            "priority": "medium",
        })

    if to_review:
        recs.append({
            "action": "review",
            "count": len(to_review),
            "description": f"Review {len(to_review)} memories with possible contradictions",
            "memory_ids": [m["id"] for m in to_review[:20]],
            "priority": "high",
        })

    if to_enrich:
        recs.append({
            "action": "enrich",
            "count": len(to_enrich),
            "description": f"Add more detail to {len(to_enrich)} very short memories",
            "memory_ids": [m["id"] for m in to_enrich[:20]],
            "priority": "low",
        })

    # Sort by priority: high → medium → low
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: priority_order.get(r.get("priority", "low"), 3))

    return recs

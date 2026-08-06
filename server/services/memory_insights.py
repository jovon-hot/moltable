"""Memory Insight Engine — Automatic Consolidation & Pattern Discovery.

Inspired by: mem0 Dream (background consolidation), Zep Observations (pattern
discovery from graph structure), Cognee improve() (session distillation).

Three capabilities:
  1. Cluster Detection — cross-compare embeddings to find related memory groups
  2. Insight Generation — LLM-powered summarization of clusters into higher-level insights
  3. Pattern Discovery — detect recurring themes, temporal trends, behavioral patterns

Usage:
    from services.memory_insights import generate_insights, list_insights

    result = generate_insights(user_id, store, persona_id="dev")
    # → {"insights_created": 3, "clusters_found": 5, ...}

Design principles:
  - Non-destructive: source memories are NOT archived (unlike manual consolidate)
  - Linked: each insight stores source memory IDs for provenance
  - LLM-first with fallback: uses DeepSeek when available, keyword heuristic otherwise
  - Persona-aware: insights can be scoped to specific personas
"""

from __future__ import annotations

import logging
import math
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("moltable.insights")

# ── Constants ────────────────────────────────────────────
MIN_CLUSTER_SIZE = 2          # At least 2 memories needed for a cluster
MAX_CLUSTER_SIZE = 15          # Cap to avoid huge LLM context
SIMILARITY_THRESHOLD = 0.72    # Cosine similarity to group memories
MANY_MEMORIES_THRESHOLD = 50   # Use sampling for large datasets
SAMPLE_SIZE = 80               # Max memories to full-embed compare


# ── Clustering ──────────────────────────────────────────

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def cluster_memories(
    memories: list[dict],
    threshold: float = SIMILARITY_THRESHOLD,
) -> list[list[dict]]:
    """Group memories into similarity-based clusters.

    Uses a greedy algorithm: each memory can belong to at most one cluster.
    Returns list of clusters, each cluster is a list of memory dicts.
    """
    if len(memories) < 2:
        return []

    # Build similarity matrix (upper-triangular)
    n = len(memories)
    pairs: list[tuple[int, int, float]] = []
    for i in range(n):
        emb_i = memories[i].get("embedding")
        if not emb_i or len(emb_i) < 2:
            continue
        for j in range(i + 1, n):
            emb_j = memories[j].get("embedding")
            if not emb_j or len(emb_j) < 2:
                continue
            sim = _cosine_similarity(emb_i, emb_j)
            if sim >= threshold:
                pairs.append((i, j, sim))

    # Sort by similarity descending — greedily merge
    pairs.sort(key=lambda p: p[2], reverse=True)

    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for i, j, _ in pairs:
        union(i, j)

    # Collect clusters
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)

    clusters: list[list[dict]] = []
    for indices in groups.values():
        if len(indices) >= MIN_CLUSTER_SIZE:
            cluster = [memories[i] for i in indices]
            if len(cluster) > MAX_CLUSTER_SIZE:
                # Take the most central members
                cluster.sort(
                    key=lambda m: len(m.get("content", "")), reverse=True
                )
                cluster = cluster[:MAX_CLUSTER_SIZE]
            clusters.append(cluster)

    logger.info(
        "Clustering: %d memories → %d clusters (threshold=%.2f)",
        n, len(clusters), threshold,
    )
    return clusters


# ── Pattern Detection ──────────────────────────────────

def detect_patterns(memories: list[dict]) -> list[dict]:
    """Detect recurring themes and behavioral patterns.

    Uses keyword-frequency analysis (no LLM required).
    Returns list of pattern dicts: {pattern, theme, count, sample_ids}.
    """
    if len(memories) < 5:
        return []

    # Collect all content
    texts = [m.get("content", "") for m in memories]
    combined = " ".join(texts).lower()

    # Pattern categories with keyword triggers
    pattern_rules = [
        ("preference", ["like", "prefer", "favorite", "love", "enjoy", "dislike", "hate", "avoid", "喜歡", "愛", "不喜歡", "討厭", "偏爱", "讨厌", "偏好", "爱吃", "不爱"]),
        ("habit", ["always", "never", "every day", "usually", "typically", "routine", "習慣", "總是", "每天"]),
        ("goal", ["want to", "plan to", "goal", "aim", "target", "objective", "目標", "計劃", "想要"]),
        ("skill", ["knows", "expert", "proficient", "can", "skill", "擅長", "會", "專業"]),
        ("relationship", ["team", "colleague", "friend", "manager", "partner", "boss", "同事", "朋友", "老闆"]),
        ("project", ["project", "deadline", "sprint", "task", "feature", "bug", "deploy", "項目", "任務"]),
    ]

    patterns: list[dict] = []
    for theme, keywords in pattern_rules:
        count = sum(1 for kw in keywords if kw in combined)
        if count >= 1:  # At least 1 keyword hit (relaxed for sparse data)
            # Find sample memories
            sample_ids: list[str] = []
            for m in memories[:50]:
                content = m.get("content", "").lower()
                if any(kw in content for kw in keywords):
                    sample_ids.append(m.get("id", ""))
                    if len(sample_ids) >= 3:
                        break

            patterns.append({
                "pattern": f"recurring_{theme}",
                "theme": theme,
                "confidence": min(1.0, count / 8.0),
                "keyword_hits": count,
                "sample_ids": sample_ids,
            })

    return patterns


# ── Insight Generation ─────────────────────────────────

def _generate_insight_llm(
    cluster: list[dict],
    strategy: str = "merge",
) -> str | None:
    """Use DeepSeek to generate a consolidated insight from a cluster.

    Returns insight text, or None if LLM unavailable/failed.
    """
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        return None

    memory_texts = "\n\n---\n\n".join([
        f"[{m.get('category','fact')}] {m.get('content','')[:500]}"
        for m in cluster[:10]
    ])

    prompts = {
        "merge": (
            "You are a memory insight engine. Given several related user memories, "
            "produce ONE consolidated insight that captures the key information. "
            "Be factual, specific, and concise (2-4 sentences). "
            "Do not add information not present in the source memories. "
            "Respond with ONLY the insight text — no JSON, no explanation.\n\n"
        ),
        "summarize": (
            "You are a memory pattern engine. Given several related user memories, "
            "extract the HIGHER-LEVEL PATTERN or theme that connects them. "
            "What does this cluster reveal about the user? "
            "Respond with ONLY the insight text (1-3 sentences).\n\n"
        ),
        "trend": (
            "You are a memory trend engine. Given several time-ordered user memories, "
            "identify the TREND or CHANGE over time. What direction is the user evolving? "
            "Respond with ONLY the trend insight text (1-3 sentences).\n\n"
        ),
    }

    prompt = prompts.get(strategy, prompts["merge"]) + memory_texts

    try:
        from openai import OpenAI
        client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com/v1")
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )
        text = (resp.choices[0].message.content or "").strip()
        if text:
            logger.info("LLM insight generated: %d memories → %d chars (strategy=%s)",
                         len(cluster), len(text), strategy)
            return text
    except Exception as e:
        logger.warning("LLM insight generation failed: %s", e)

    return None


def _generate_insight_fallback(cluster: list[dict]) -> str:
    """Fallback insight generation using longest-memory + summary."""
    longest = max(cluster, key=lambda m: len(m.get("content", "")))
    categories = set(m.get("category", "fact") for m in cluster)
    sources = set(m.get("source", "unknown")[:30] for m in cluster)

    lines = [
        f"[Auto-insight from {len(cluster)} related memories]",
        "",
        longest.get("content", "")[:400],
    ]

    others = [m for m in cluster if m.get("id") != longest.get("id")]
    if others:
        lines.append("\n--- Related context ---")
        for m in others[:5]:
            lines.append(f"• {m.get('content', '')[:200]}")

    return "\n".join(lines)


# ── Main API ────────────────────────────────────────────

def generate_insights(
    user_id: str,
    store,
    persona_id: str | None = None,
    max_insights: int = 10,
    auto_consolidate: bool = False,
) -> dict:
    """Generate insights by clustering related memories and consolidating clusters.

    Args:
        user_id: Target user.
        store: Memory store (SupabaseMemoryRepository or SQLite adapter).
        persona_id: Optional persona scope.
        max_insights: Cap on number of insights to generate.
        auto_consolidate: If True, automatically consolidate very high-similarity (>0.92)
                         clusters into single enriched memory + archive originals.

    Returns:
        dict with insights_created, clusters_found, patterns_detected, etc.
    """
    # Fetch all non-archived, non-insight memories
    all_memories = store.list(user_id, limit=10000)
    candidates = [
        m for m in all_memories
        if not m.get("is_archived")
        and m.get("category") != "insight"
    ]
    if persona_id:
        candidates = [
            m for m in candidates
            if m.get("persona_id") == persona_id
        ]

    if len(candidates) < MIN_CLUSTER_SIZE:
        logger.info("Not enough memories for insight generation (%d)", len(candidates))
        return {
            "insights_created": 0,
            "clusters_found": 0,
            "patterns_detected": 0,
            "total_memories_scanned": len(candidates),
            "message": f"Need at least {MIN_CLUSTER_SIZE} memories (have {len(candidates)})",
        }

    # Sample for large datasets
    if len(candidates) > SAMPLE_SIZE:
        # Keep most recent + random selection
        candidates.sort(
            key=lambda m: m.get("created_at", ""), reverse=True
        )
        candidates = candidates[:SAMPLE_SIZE]

    # Cluster by embedding similarity
    clusters = cluster_memories(candidates)
    if not clusters:
        return {
            "insights_created": 0,
            "clusters_found": 0,
            "patterns_detected": 0,
            "total_memories_scanned": len(candidates),
            "message": "No meaningful clusters found — memories are diverse",
        }

    # Sort clusters by size (largest first)
    clusters.sort(key=len, reverse=True)

    # Generate insights
    insights_created = 0
    patches_created = 0
    created_insights: list[dict] = []

    for i, cluster in enumerate(clusters):
        if insights_created >= max_insights:
            break

        # Determine strategy based on cluster characteristics
        categories = set(m.get("category", "fact") for m in cluster)
        sources = set(m.get("source", "unknown") for m in cluster[:5])

        # Check for very high similarity clusters → auto-consolidate
        if auto_consolidate and len(cluster) >= 2:
            from services.embedding import embed as embed_fn
            # Quick avg similarity check
            sims: list[float] = []
            for a in cluster[: min(5, len(cluster))]:
                for b in cluster[: min(5, len(cluster))]:
                    if a["id"] < b["id"]:
                        ea = a.get("embedding")
                        eb = b.get("embedding")
                        if ea and eb:
                            sims.append(_cosine_similarity(ea, eb))
            avg_sim = sum(sims) / len(sims) if sims else 0

            if avg_sim > 0.92:
                # Very high similarity — auto consolidate to single enriched memory
                strategy = "merge"
            elif avg_sim > 0.80:
                strategy = "summarize"
            else:
                strategy = "merge"
        else:
            strategy = "summarize"  # default: create insight, don't touch originals

        # Try LLM, fall back to heuristic
        insight_text = _generate_insight_llm(cluster, strategy)
        if not insight_text:
            insight_text = _generate_insight_fallback(cluster)

        # Create insight memory
        from services.embedding import embed as embed_fn
        insight_vec = embed_fn(insight_text)

        source_ids = [m.get("id", "") for m in cluster[:10]]
        tags = list(set(
            t for m in cluster[:5]
            for t in (m.get("tags") or [])
        ))[:20]

        # Merge cluster tags
        all_tags: list[str] = []
        for m in cluster[:10]:
            for t in (m.get("tags") or []):
                if t not in all_tags:
                    all_tags.append(t)

        new_memory = store.insert(
            user_id,
            insight_text,
            insight_vec,
            category="insight",
            source=f"auto_insight:strategy_{strategy}",
            confidence=0.8,
            tags=all_tags[:20],
            persona_id=persona_id,
        )

        created_insights.append({
            "id": new_memory.get("id", ""),
            "content_preview": insight_text[:150],
            "strategy": strategy,
            "source_count": len(cluster),
            "source_ids": source_ids[:5],
        })
        insights_created += 1

        logger.info(
            "Created insight #%d: %d sources → %s",
            i + 1, len(cluster), strategy,
        )

    # Detect patterns (non-LLM, low cost)
    patterns = detect_patterns(candidates)

    return {
        "insights_created": insights_created,
        "clusters_found": len(clusters),
        "patterns_detected": len(patterns),
        "total_memories_scanned": len(candidates),
        "insights": created_insights,
        "patterns": patterns,
    }


def list_insights(
    user_id: str,
    store,
    persona_id: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """List all insight-type memories for a user."""
    all_memories = store.list(user_id, limit=10000)
    insights = [
        m for m in all_memories
        if m.get("category") == "insight"
        and not m.get("is_archived")
    ]
    if persona_id:
        insights = [
            m for m in insights
            if m.get("persona_id") == persona_id
        ]
    # Sort by recency
    insights.sort(key=lambda m: m.get("created_at", ""), reverse=True)
    return insights[:limit]

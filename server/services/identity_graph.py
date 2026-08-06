"""Identity Graph Service — context-aware memory retrieval engine.

Implements the Identity Graph query resolution flow:
  1. Identity resolution (who is the user?)
  2. Persona routing (which Persona is active?)
  3. Project scoping (which Project is active?)
  4. Graph traversal (filter memories by relationships)
  5. Temporal weighting (apply recency decay)
  6. Context assembly (combine all context for the agent)

This service integrates with the existing knowledge_graph service and the
relationship inference engine to deliver contextually relevant memories,
preferences, and constraints for any agent session.
"""

from __future__ import annotations

import logging
import math
import time
from typing import Any, Dict, List, Optional, Tuple

from services.knowledge_graph import knowledge_graph_service
from services.relationship_inference import (
    infer_relationships,
    relationship_summary,
    sanitize_relationship_data,
)

logger = logging.getLogger("moltable.identity_graph")

# ── Temporal decay constants ────────────────────────────────
DECAY_HALF_LIFE_DAYS = 7.0             # Exponential decay half-life
DECAY_LAMBDA = math.log(2) / DECAY_HALF_LIFE_DAYS  # Decay rate constant
FRESH_BOOST_DAYS = 7.0                  # Memories accessed within this get 1.2x
FRESH_BOOST_MULTIPLIER = 1.2
SUPERSEDED_PENALTY_MULTIPLIER = 0.1     # Marked superseded → 90% penalty
ACTIVE_PROJECT_BOOST = 1.1              # Active project scoped → 10% boost
PINNED_IMMUNITY = True                  # Pinned memories ignore decay


def _temporal_decay_weight(
    memory: dict,
    now_ts: Optional[float] = None,
    is_superseded: bool = False,
    is_pinned: bool = False,
    is_active_project: bool = False,
) -> float:
    """Calculate temporal decay weight for a single memory.

    Args:
        memory: Memory dict with created_at (ISO timestamp) and optional
                last_accessed, confidence fields.
        now_ts: Current Unix timestamp (defaults to now).
        is_superseded: If True, applies 0.1x penalty.
        is_pinned: If True, returns 1.0 (immune to decay).
        is_active_project: If True, applies 1.1x boost.

    Returns:
        Weight between 0.0 and ~1.5 (with boosts).
    """
    if is_pinned and PINNED_IMMUNITY:
        return 1.0

    if now_ts is None:
        now_ts = time.time()

    # Base confidence
    confidence = float(memory.get("confidence", 1.0))

    # Time decay: use last_accessed if available, else created_at
    timestamp_str = memory.get("last_accessed") or memory.get("created_at", "")
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        age_seconds = max(0, now_ts - dt.timestamp())
    except Exception:
        age_seconds = DECAY_HALF_LIFE_DAYS * 86400  # default to half-life age

    age_days = age_seconds / 86400.0
    decay = math.exp(-DECAY_LAMBDA * age_days)

    weight = confidence * decay

    # Fresh boost: accessed within FRESH_BOOST_DAYS
    if age_days <= FRESH_BOOST_DAYS and not is_superseded:
        weight *= FRESH_BOOST_MULTIPLIER

    # Superseded penalty
    if is_superseded:
        weight *= SUPERSEDED_PENALTY_MULTIPLIER

    # Active project boost
    if is_active_project:
        weight *= ACTIVE_PROJECT_BOOST

    return round(weight, 4)


class IdentityGraphService:
    """Context-aware memory retrieval with graph traversal and temporal decay.

    Usage:
        svc = IdentityGraphService(memory_store)
        context = svc.query(user_id, query="review auth module",
                            persona="code-reviewer", project="project-x")
    """

    def __init__(self, memory_store):
        """Initialize with a memory store (VectorStore or SupabaseMemoryRepository).

        Args:
            memory_store: Object with .list(user_id, ...) and .search(user_id, vec, ...).
        """
        self.store = memory_store
        self._relationship_cache: Dict[str, Tuple[float, dict]] = {}
        self._cache_ttl = 300  # 5 minutes

    # ── Identity Graph Query ──────────────────────────────
    def query(
        self,
        user_id: str,
        query: str,
        persona: Optional[str] = None,
        project: Optional[str] = None,
        top_k: int = 10,
        include_preferences: bool = True,
        include_relationships: bool = True,
    ) -> dict:
        """Execute an Identity Graph-aware query.

        Args:
            user_id: The user's identity ID.
            query: Natural language search query.
            persona: Active Persona name (for context filtering).
            project: Active Project name (for scope filtering).
            top_k: Max memories to return.
            include_preferences: Include scoped preferences in context.
            include_relationships: Include relationship data in results.

        Returns:
            {
                "memories": [...],
                "preferences": [...],
                "graph_context": {...},
                "relationships": {...},
                "stats": {...},
            }
        """
        from services.embedding import embed

        query_vec = embed(query)

        # Step 1: Get candidate memories (all user memories)
        all_memories = self.store.list(user_id, limit=500)
        if not all_memories:
            return {
                "memories": [],
                "preferences": [],
                "graph_context": {},
                "relationships": {},
                "stats": {"total_memories": 0, "filtered": 0, "returned": 0},
            }

        # Step 2: Persona filtering (if active Persona provided)
        persona_filtered = all_memories
        if persona:
            persona_lower = persona.lower().strip()
            persona_filtered = [
                m for m in all_memories
                if self._matches_persona(m, persona_lower)
            ]
            # If too few persona-specific memories, fall back to all
            if len(persona_filtered) < max(3, top_k // 2):
                persona_filtered = all_memories

        # Step 3: Project scoping (if active Project provided)
        project_filtered = persona_filtered
        if project:
            project_lower = project.lower().strip()
            project_filtered = [
                m for m in persona_filtered
                if self._matches_project(m, project_lower)
            ]
            if len(project_filtered) < max(3, top_k // 2):
                project_filtered = persona_filtered

        # Step 4: Graph traversal — filter by related entities
        graph_memories = self._graph_traverse(user_id, project_filtered)

        # Step 5: Temporal weighting
        now_ts = time.time()
        weighted = []
        for m in graph_memories:
            weight = _temporal_decay_weight(
                m,
                now_ts=now_ts,
                is_superseded=m.get("_superseded", False),
                is_pinned=m.get("pinned", False),
                is_active_project=bool(project and self._matches_project(m, project.lower().strip()) if project else False),
            )
            # Blend: vector similarity (70%) + temporal weight (30%)
            weighted.append((m, weight))

        # Step 6: Vector search on filtered set
        if len(weighted) <= top_k:
            # Few results, return all with temporal scoring
            results = []
            for m, tw in weighted:
                results.append(self._format_memory(m, temporal_weight=tw))
        else:
            # Compute similarity against query_vec for each candidate
            scored = []
            for m, tw in weighted:
                emb = m.get("embedding")
                if emb:
                    sim = _cosine_similarity(query_vec, emb)
                    combined = 0.7 * sim + 0.3 * max(0, tw)
                else:
                    combined = tw * 0.5  # No embedding → rely on temporal
                scored.append((combined, m, tw))

            scored.sort(key=lambda x: x[0], reverse=True)
            results = [
                self._format_memory(s[1], temporal_weight=s[2], relevance=s[0])
                for s in scored[:top_k]
            ]

        # Step 7: Build context
        context = {
            "memories": results,
            "preferences": self._get_preferences(user_id, persona, project) if include_preferences else [],
            "graph_context": self._build_graph_context(user_id, [r["id"] for r in results]),
            "relationships": self._get_relationships(
                user_id, [r["id"] for r in results]
            ) if include_relationships else {},
            "stats": {
                "total_memories": len(all_memories),
                "persona_filtered": len(persona_filtered),
                "project_filtered": len(project_filtered),
                "graph_filtered": len(graph_memories),
                "returned": len(results),
            },
        }

        return context

    # ── Persona matching ──────────────────────────────────
    def _matches_persona(self, memory: dict, persona_name: str) -> bool:
        """Check if memory is relevant to a Persona."""
        persona_id = memory.get("persona_id", "")
        if persona_id:
            # Direct persona association
            if persona_name in str(persona_id).lower():
                return True

        # Check tags and content for persona references
        tags = memory.get("tags") or []
        for tag in tags:
            if persona_name in str(tag).lower():
                return True

        # Content matching (lightweight)
        content = (memory.get("content") or "").lower()
        if persona_name in content:
            return True

        return False

    # ── Project matching ──────────────────────────────────
    def _matches_project(self, memory: dict, project_name: str) -> bool:
        """Check if memory is scoped to a project."""
        # Direct project_id
        project_id = memory.get("project_id", "")
        if project_id and project_name in str(project_id).lower():
            return True

        # Check tags
        tags = memory.get("tags") or []
        for tag in tags:
            if project_name in str(tag).lower():
                return True

        # Content matching
        content = (memory.get("content") or "").lower()
        if project_name in content:
            return True

        return False

    # ── Graph traversal ────────────────────────────────────
    def _graph_traverse(self, user_id: str, memories: List[dict]) -> List[dict]:
        """Filter/boost memories using knowledge graph connections.

        Memories connected to highly active entities get a slight boost.
        """
        try:
            graph = knowledge_graph_service.get_graph(user_id)
        except Exception:
            return memories  # KG unavailable → pass through

        if not graph.get("nodes"):
            return memories

        # Build entity → weight map
        entity_weights: Dict[str, float] = {}
        for node in graph.get("nodes", []):
            count = node.get("count", 1)
            entity_weights[node["name"]] = math.log(1 + count)  # log-scale weight

        # Score each memory by accumulated entity weight
        scored = []
        now_ts = time.time()
        for m in memories:
            content = (m.get("content") or "").lower()
            tags = [t.lower() for t in (m.get("tags") or [])]

            # Count matching entities
            entity_score = 0.0
            match_count = 0
            for entity, weight in entity_weights.items():
                entity_lower = entity.lower()
                if entity_lower in content or entity_lower in tags:
                    entity_score += weight
                    match_count += 1

            # Superseded detection via KG
            is_superseded = self._check_superseded(user_id, m.get("id", ""))

            scored.append({
                **m,
                "_entity_score": round(entity_score, 2),
                "_match_count": match_count,
                "_superseded": is_superseded,
            })

        # Sort by entity score (more connected → more relevant)
        scored.sort(key=lambda x: x["_entity_score"], reverse=True)
        return scored

    # ── Superseded check ────────────────────────────────────
    def _check_superseded(self, user_id: str, memory_id: str) -> bool:
        """Check if a memory has been superseded."""
        # Check cache first
        cache_key = f"{user_id}:superseded"
        cached_ts, cached_data = self._relationship_cache.get(cache_key, (0, {}))
        if time.time() - cached_ts < self._cache_ttl:
            return memory_id in cached_data.get("superseded_ids", set())

        # Lazy computation: check all memories for supersede relationships
        try:
            all_memories = self.store.list(user_id, limit=500)
            superseded_ids = set()
            for m in all_memories:
                sid = m.get("supersedes_id")
                if sid:
                    superseded_ids.add(str(sid))

            self._relationship_cache[cache_key] = (
                time.time(),
                {"superseded_ids": superseded_ids},
            )
            return memory_id in superseded_ids
        except Exception:
            return False

    # ── Preferences ─────────────────────────────────────────
    def _get_preferences(
        self, user_id: str, persona: Optional[str], project: Optional[str]
    ) -> List[dict]:
        """Get scoped preferences for the active context."""
        try:
            all_memories = self.store.list(user_id, limit=500)
        except Exception:
            return []

        prefs = []
        for m in all_memories:
            if m.get("category") != "preference":
                continue
            content = (m.get("content") or "").strip()
            if not content:
                continue

            # Scope filtering
            tags = [t.lower() for t in (m.get("tags") or [])]
            is_global = "global" in tags or not any(
                t in tags for t in ["persona:", "project:"]
            )
            is_persona_match = persona and any(
                f"persona:{persona.lower()}" in t for t in tags
            )
            is_project_match = project and any(
                f"project:{project.lower()}" in t for t in tags
            )

            if is_global or is_persona_match or is_project_match:
                prefs.append({
                    "key": m.get("tags", [None])[0] if m.get("tags") else None,
                    "value": content,
                    "confidence": m.get("confidence", 1.0),
                    "source": m.get("source", ""),
                })

        return prefs

    # ── Graph context ───────────────────────────────────────
    def _build_graph_context(
        self, user_id: str, memory_ids: List[str]
    ) -> dict:
        """Build graph context for the retrieved memories."""
        try:
            graph = knowledge_graph_service.get_graph(user_id)
        except Exception:
            return {"nodes": [], "edges": [], "stats": {}}

        # Filter to entities connected to retrieved memories
        relevant_nodes = set()
        relevant_edges = []

        for m_id in memory_ids:
            for edge in graph.get("edges", []):
                if m_id in edge.get("memories", []):
                    relevant_nodes.add(edge["source"])
                    relevant_nodes.add(edge["target"])
                    relevant_edges.append(edge)

        return {
            "nodes": [
                n for n in graph.get("nodes", [])
                if n["name"] in relevant_nodes
            ],
            "edges": relevant_edges,
            "stats": {
                "total_nodes": graph.get("stats", {}).get("nodes", 0),
                "relevant_nodes": len(relevant_nodes),
                "relevant_edges": len(relevant_edges),
            },
        }

    # ── Relationships ───────────────────────────────────────
    def _get_relationships(
        self, user_id: str, memory_ids: List[str]
    ) -> dict:
        """Get relationship data for retrieved memories."""
        # Detect relationships among the retrieved set
        try:
            all_memories = self.store.list(user_id, limit=500)
            memories_map = {str(m.get("id", "")): m for m in all_memories}
        except Exception:
            return {"supersedes": [], "contradicts": [], "extends": []}

        retrieved = [memories_map[mid] for mid in memory_ids if mid in memories_map]
        if len(retrieved) < 2:
            return {"supersedes": [], "contradicts": [], "extends": []}

        # Compare each pair
        relationships = {"supersedes": [], "contradicts": [], "extends": []}
        for i in range(len(retrieved)):
            for j in range(i + 1, len(retrieved)):
                result = infer_relationships(
                    retrieved[i],
                    [retrieved[j]],
                )
                for rel_type in relationships:
                    if result.get(rel_type):
                        relationships[rel_type].extend(result[rel_type])

        return relationships

    # ── Formatting ──────────────────────────────────────────
    def _format_memory(
        self, memory: dict, temporal_weight: float = 1.0, relevance: float = 0.5
    ) -> dict:
        """Format a memory for API response."""
        return {
            "id": memory.get("id"),
            "content": memory.get("content"),
            "category": memory.get("category", "fact"),
            "source": memory.get("source", ""),
            "tags": memory.get("tags") or [],
            "confidence": memory.get("confidence", 1.0),
            "relevance": round(relevance, 4),
            "temporal_weight": round(temporal_weight, 4),
            "created_at": str(memory.get("created_at", "")),
            "superseded": memory.get("_superseded", False),
            "entity_score": memory.get("_entity_score", 0),
        }

    # ── Auto Provision (one-shot identity restoration) ─────
    def auto_provision(
        self, user_id: str, agent: str, device: Optional[str] = None
    ) -> dict:
        """One-shot identity restoration for a new agent session.

        Returns complete context snapshot: active Persona, preferences,
        top memories, and graph context.
        """
        # Determine best active Persona
        active_persona = self._detect_active_persona(user_id, agent)

        # Get top memories
        context = self.query(
            user_id,
            query=f"agent setup {agent}",
            persona=active_persona,
            top_k=20,
            include_preferences=True,
            include_relationships=False,  # Skip for speed
        )

        return {
            "agent": agent,
            "device": device,
            "persona": active_persona,
            "preferences": context.get("preferences", []),
            "recent_memories": context.get("memories", [])[:10],
            "graph_summary": {
                "total_nodes": context.get("graph_context", {}).get("stats", {}).get("total_nodes", 0),
                "relevant_nodes": context.get("graph_context", {}).get("stats", {}).get("relevant_nodes", 0),
            },
        }

    def _detect_active_persona(
        self, user_id: str, agent: str
    ) -> Optional[str]:
        """Detect the best active Persona for an agent."""
        try:
            from app_state import supabase as sb
            resp = sb.table("personas").select("name").eq(
                "user_id", user_id
            ).eq("is_active", True).limit(1).execute()
            if resp.data:
                return resp.data[0].get("name")
        except Exception:
            pass

        # Fallback: guess from agent type
        agent_persona_map = {
            "claude": "developer",
            "codex": "developer",
            "hermes": "administrator",
            "cursor": "developer",
            "chatgpt": "general",
        }
        return agent_persona_map.get(agent.lower(), "general")

    # ── Stats ───────────────────────────────────────────────
    def get_identity_stats(self, user_id: str) -> dict:
        """Get Identity Graph stats for a user."""
        try:
            graph = knowledge_graph_service.get_graph(user_id)
            memories = self.store.list(user_id, limit=0)  # Just count
        except Exception:
            return {"error": "Store unavailable"}

        # Count relationships
        superseded_count = 0
        for m in memories:
            if m.get("supersedes_id"):
                superseded_count += 1

        return {
            "total_memories": len(memories),
            "graph_nodes": graph.get("stats", {}).get("nodes", 0),
            "graph_edges": graph.get("stats", {}).get("edges", 0),
            "superseded_memories": superseded_count,
            "memory_health": self._calc_memory_health(memories),
        }

    def _calc_memory_health(self, memories: List[dict]) -> dict:
        """Quick health assessment of user's memories."""
        if not memories:
            return {"score": 100, "issues": []}

        now_ts = time.time()
        stale_count = 0
        for m in memories:
            ts = m.get("created_at", "")
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                age_days = (now_ts - dt.timestamp()) / 86400.0
                if age_days > 30:
                    stale_count += 1
            except Exception:
                pass

        stale_pct = stale_count / len(memories) * 100
        score = max(0, 100 - stale_pct * 2)

        issues = []
        if stale_pct > 30:
            issues.append(f"{stale_pct:.0f}% of memories are 30+ days old")
        if len(memories) > 100:
            issues.append(f"Memory count high ({len(memories)}), consider cleanup")

        return {"score": round(score, 1), "issues": issues}


# ── Cosine similarity helper ───────────────────────────────
def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── Module-level singleton ──────────────────────────────────
identity_graph_service: Optional[IdentityGraphService] = None


def get_identity_graph() -> IdentityGraphService:
    """Get or create the Identity Graph service singleton."""
    global identity_graph_service
    if identity_graph_service is None:
        from app_state import get_store
        identity_graph_service = IdentityGraphService(get_store())
    return identity_graph_service

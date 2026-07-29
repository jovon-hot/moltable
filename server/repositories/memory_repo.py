"""Supabase pgvector repository — persistent memory storage"""
from __future__ import annotations
from typing import List, Dict, Optional
import time, uuid

from services.repository import Repository
from services.embedding import embed as _embed_service


def _cosine_sim(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _parse_tags(tags_val) -> List[str]:
    """Parse tags from DB value (could be JSON string or list)."""
    if not tags_val:
        return []
    if isinstance(tags_val, list):
        return tags_val
    if isinstance(tags_val, str):
        try:
            import json
            parsed = json.loads(tags_val)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []
    return []


class SupabaseMemoryRepository(Repository):
    """PostgreSQL + pgvector backed memory repository using Supabase REST API

    Uses the existing ``supabase`` client from ``app_state``.
    Falls back gracefully to the in-memory store if Supabase is unavailable.
    """

    def __init__(self, supabase_client, fallback_store=None):
        self._supabase = supabase_client
        self._fallback = fallback_store  # in-memory VectorStore as cache/fallback
        self._offline = supabase_client is None

    # ── helpers ──────────────────────────────────────────

    @staticmethod
    def _now() -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def _short_id() -> str:
        return str(uuid.uuid4())[:8]

    def _dict_from_row(self, row: dict) -> dict:
        """Normalise a Supabase row dict to the same shape as VectorStore returns.
        
        Handles both SQLite (JSON-string) and Supabase (native JSON) formats.
        """
        import json

        def _maybe_parse(val):
            """Parse JSON string to list if needed."""
            if isinstance(val, str) and val.startswith("["):
                try:
                    return json.loads(val)
                except Exception:
                    return val
            return val

        return {
            "id": str(row.get("id", "")),
            "user_id": str(row.get("user_id", "")),
            "content": row.get("content", ""),
            "embedding": _maybe_parse(row.get("embedding", [])),
            "category": row.get("category", "fact"),
            "source": row.get("source", "manual"),
            "confidence": float(row.get("confidence", 1.0)),
            "tags": _maybe_parse(row.get("tags") or []),
            "is_archived": bool(row.get("is_archived", False)),
            "created_at": row.get("created_at", ""),
        }

    # ── Primary: Supabase backed ─────────────────────────

    def insert(self, user_id: str, content: str, embedding: List[float],
               category: str = "fact", source: str = "manual",
               confidence: float = 1.0, tags: List[str] | None = None) -> Dict:
        if self._offline:
            if self._fallback:
                return self._fallback.insert(user_id, content, embedding,
                                             category, source, confidence, tags)
            raise RuntimeError("Supabase offline and no fallback available")

        payload = {
            "id": self._short_id(),
            "user_id": user_id,
            "content": content,
            "category": category,
            "source": source,
            "confidence": confidence,
            "embedding": embedding,
            "tags": tags or [],
        }
        resp = self._supabase.table("memories").insert(payload).execute()
        if resp.data:
            return self._dict_from_row(resp.data[0])
        raise RuntimeError(f"Failed to insert memory: {resp}")

    def get(self, memory_id: str, user_id: str) -> Optional[Dict]:
        if self._offline:
            return self._fallback.get(memory_id, user_id) if self._fallback else None

        resp = self._supabase.table("memories") \
            .select("*") \
            .eq("id", memory_id) \
            .eq("user_id", user_id) \
            .eq("is_archived", False) \
            .limit(1) \
            .execute()
        if resp.data:
            return self._dict_from_row(resp.data[0])
        return None

    def list(self, user_id: str, category: Optional[str] = None,
             limit: int = 50) -> List[Dict]:
        if self._offline:
            return self._fallback.list(user_id, category, limit) if self._fallback else []

        query = self._supabase.table("memories") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("is_archived", False) \
            .order("created_at", desc=True) \
            .limit(limit)
        if category:
            query = query.eq("category", category)
        resp = query.execute()
        return [self._dict_from_row(r) for r in (resp.data or [])]

    def update(self, memory_id: str, user_id: str, **kwargs) -> bool:
        if self._offline:
            return self._fallback.update(memory_id, user_id, **kwargs) if self._fallback else False

        # Build update payload (skip None values)
        payload = {}
        for k in ("content", "category", "source", "confidence", "tags", "is_archived", "embedding"):
            if k in kwargs and kwargs[k] is not None:
                payload[k] = kwargs[k]
        if not payload:
            return False

        resp = self._supabase.table("memories") \
            .update(payload) \
            .eq("id", memory_id) \
            .eq("user_id", user_id) \
            .execute()
        return len(resp.data or []) > 0

    def delete(self, memory_id: str, user_id: str) -> bool:
        if self._offline:
            return self._fallback.delete(memory_id, user_id) if self._fallback else False

        # Soft-delete: set is_archived = True
        resp = self._supabase.table("memories") \
            .update({"is_archived": True}) \
            .eq("id", memory_id) \
            .eq("user_id", user_id) \
            .execute()
        return len(resp.data or []) > 0

    # ── Vector Search via pgvector RPC ───────────────────

    def search(self, user_id: str, query_embedding: List[float],
               top_k: int = 5, threshold: float = 0.5,
               category: Optional[str] = None) -> List[Dict]:
        if self._offline:
            return self._fallback.search(user_id, query_embedding, top_k, threshold, category) \
                if self._fallback else []

        try:
            resp = self._supabase.rpc("match_memories", {
                "query_embedding": query_embedding,
                "match_user_id": user_id,
                "match_count": top_k,
                "match_category": category,
                "match_threshold": threshold,
            }).execute()

            results = []
            for r in (resp.data or []):
                results.append({
                    "id": str(r.get("id", "")),
                    "user_id": user_id,
                    "content": r.get("content", ""),
                    "category": r.get("category", ""),
                    "source": r.get("source", ""),
                    "tags": r.get("tags") or [],
                    "similarity": round(float(r.get("similarity", 0)), 4),
                    "created_at": r.get("created_at", ""),
                })
            return results
        except Exception as exc:
            # Fallback to in-memory search on RPC failure
            if self._fallback:
                return self._fallback.search(user_id, query_embedding, top_k, threshold, category)
            # SQLite mode: load all memories and return by recency
            # (trigram hash embeddings are too sparse for cosine similarity)
            try:
                all_memories = self.list(user_id, category=category, limit=10000)
                if not all_memories:
                    return []
                results = []
                for mem in all_memories[:top_k]:
                    results.append({
                        "id": mem["id"],
                        "user_id": user_id,
                        "content": mem["content"],
                        "category": mem.get("category", ""),
                        "source": mem.get("source", ""),
                        "tags": _parse_tags(mem.get("tags")),
                        "similarity": 0.5,  # dummy score for SQLite mode
                        "created_at": mem.get("created_at", ""),
                    })
                return results
            except Exception:
                return []

    def find_conflicts(self, user_id: str, query_embedding: List[float],
                       top_k: int = 3) -> List[Dict]:
        return self.search(user_id, query_embedding, top_k=top_k, threshold=0.85)

    def stats(self, user_id: str) -> Dict:
        if self._offline:
            return self._fallback.stats(user_id) if self._fallback else {"total": 0, "archived": 0}

        total_q = self._supabase.table("memories") \
            .select("count", count="exact") \
            .eq("user_id", user_id) \
            .eq("is_archived", False) \
            .limit(1)

        archived_q = self._supabase.table("memories") \
            .select("count", count="exact") \
            .eq("user_id", user_id) \
            .eq("is_archived", True) \
            .limit(1)

        total_resp = total_q.execute()
        archived_resp = archived_q.execute()

        return {
            "total": total_resp.count if hasattr(total_resp, 'count') else 0,
            "archived": archived_resp.count if hasattr(archived_resp, 'count') else 0,
        }

    def migrate_user(self, from_user_id: str, to_user_id: str) -> int:
        if self._offline:
            if self._fallback:
                return self._fallback.migrate_user(from_user_id, to_user_id)
            return 0

        # Update all memories with session user_id to real user UUID
        resp = self._supabase.table("memories") \
            .update({"user_id": to_user_id}) \
            .eq("user_id", from_user_id) \
            .execute()
        return len(resp.data or [])

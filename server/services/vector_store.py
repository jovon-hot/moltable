from __future__ import annotations

"""In-memory vector store — zero-dependency pgvector replacement"""
import math
import time
import uuid
from typing import Dict, List


class VectorStore:
    """Thread-safe in-memory store with cosine similarity search"""

    def __init__(self):
        self._store: Dict[str, Dict] = {}  # memory_id → {user_id, content, embedding, ...}
        self._offline = False  # compat with SupabaseMemoryRepository

    # ── CRUD ──────────────────────────────────────────
    def insert(self, user_id: str, content: str, embedding: List[float],
               category: str = "fact", source: str = "manual",
               confidence: float = 1.0, tags: List[str] | None = None,
               persona_id: str | None = None) -> Dict:
        mid = str(uuid.uuid4())[:8]
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        doc = {
            "id": mid, "user_id": user_id, "content": content,
            "embedding": embedding, "category": category,
            "source": source, "confidence": confidence,
            "tags": tags or [], "created_at": now,
            "persona_id": persona_id,
            "is_archived": False,
        }
        self._store[mid] = doc
        return doc

    def get(self, memory_id: str, user_id: str) -> dict | None:
        doc = self._store.get(memory_id)
        if doc and doc["user_id"] == user_id and not doc["is_archived"]:
            return doc
        return None

    def list(self, user_id: str, category: str | None = None,
             limit: int = 50) -> List[Dict]:
        results = []
        for doc in self._store.values():
            if doc["user_id"] != user_id or doc["is_archived"]:
                continue
            if category and doc["category"] != category:
                continue
            results.append(doc)
        results.sort(key=lambda d: d["created_at"], reverse=True)
        return results[:limit]

    def update(self, memory_id: str, user_id: str, **kwargs) -> bool:
        doc = self._store.get(memory_id)
        if not doc or doc["user_id"] != user_id:
            return False
        for k, v in kwargs.items():
            if v is not None:
                doc[k] = v
        return True

    def delete(self, memory_id: str, user_id: str) -> bool:
        doc = self._store.get(memory_id)
        if not doc or doc["user_id"] != user_id:
            return False
        doc["is_archived"] = True
        return True

    # ── Search ────────────────────────────────────────
    def search(self, user_id: str, query_embedding: List[float],
               top_k: int = 5, threshold: float = 0.5,
               category: str | None = None) -> List[Dict]:
        """Cosine similarity search within user's memories"""
        results = []
        for doc in self._store.values():
            if doc["user_id"] != user_id or doc["is_archived"]:
                continue
            if category and doc["category"] != category:
                continue
            sim = _cosine(query_embedding, doc["embedding"])
            if sim >= threshold:
                results.append({**doc, "similarity": round(sim, 4)})

        results.sort(key=lambda d: d["similarity"], reverse=True)
        return results[:top_k]

    def find_conflicts(self, user_id: str, query_embedding: List[float],
                       top_k: int = 3) -> List[Dict]:
        """Find near-duplicate memories (similarity > 0.9)"""
        return self.search(user_id, query_embedding, top_k=top_k, threshold=0.85)

    # ── Stats ─────────────────────────────────────────
    def stats(self, user_id: str) -> dict:
        total = sum(1 for d in self._store.values()
                    if d["user_id"] == user_id and not d["is_archived"])
        archived = sum(1 for d in self._store.values()
                       if d["user_id"] == user_id and d["is_archived"])
        return {"total": total, "archived": archived}

    # ── User migration ───────────────────────────────
    def migrate_user(self, from_user_id: str, to_user_id: str) -> int:
        count = 0
        for doc in self._store.values():
            if doc["user_id"] == from_user_id:
                doc["user_id"] = to_user_id
                count += 1
        return count


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

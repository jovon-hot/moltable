from __future__ import annotations
"""Memory routes — CRUD + semantic search with in-memory vector store"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from app_state import limiter, get_store
from routes.auth import get_user
from services.embedding import embed

router = APIRouter(prefix="/api/memories", tags=["memories"])


class MemoryCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Memory content")
    category: str = Field(default="fact", pattern=r"^(preference|decision|fact|project|insight|task|relationship)$")
    source: str = Field(default="manual", max_length=200)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    tags: list[str] = Field(default=[], max_length=50)


class MemoryUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=10000)
    category: str | None = Field(default=None, pattern=r"^(preference|decision|fact|project|insight|task|relationship)$")
    is_archived: bool | None = None
    tags: list[str] | None = Field(default=None, max_length=50)


# ── Save ──────────────────────────────────────────────
@router.post("")
@limiter.limit("60/minute")
def save_memory(request: Request, body: MemoryCreate, force: bool = Query(False),
                user_id: str = Depends(get_user)):
    # ── 配额检查（按 plan 动态限额） ─────────────────
    from services.quota import check_quota
    existing = get_store().list(user_id, limit=0)
    count = len(existing)
    check_quota(user_id, "memories", count)
    vec = embed(body.content)

    if not force:
        conflicts = get_store().find_conflicts(user_id, vec)
        strong = [c for c in conflicts if c["similarity"] > 0.9]
        if strong:
            return {
                "saved": False, "conflict": True,
                "existing": [{"id": c["id"], "content": c["content"][:100],
                               "similarity": c["similarity"]} for c in strong],
                "message": "Similar memories found. Use ?force=true to overwrite.",
            }

    doc = get_store().insert(
        user_id, body.content, vec,
        category=body.category, source=body.source,
        confidence=body.confidence, tags=body.tags,
    )
    return {"saved": True, "id": doc["id"]}


# ── Search ────────────────────────────────────────────
@router.get("/search")
@limiter.limit("120/minute")
def search_memory(request: Request, q: str = Query(..., min_length=1, max_length=500),
                  category: str | None = None, top_k: int = Query(default=5, ge=1, le=50),
                  user_id: str = Depends(get_user)):
    vec = embed(q)
    results = get_store().search(user_id, vec, top_k=top_k, category=category)
    return {
        "query": q,
        "results": [{
            "id": r["id"], "content": r["content"],
            "category": r["category"], "source": r["source"],
            "relevance": r["similarity"],
            "created_at": r.get("created_at", ""),
        } for r in results],
    }


# ── CRUD ──────────────────────────────────────────────
@router.get("")
@limiter.limit("120/minute")
def list_memories(request: Request, category: str | None = None,
                  limit: int = Query(default=50, ge=1, le=200),
                  user_id: str = Depends(get_user)):
    return get_store().list(user_id, category=category, limit=limit)


@router.get("/{memory_id}")
@limiter.limit("120/minute")
def get_memory(request: Request, memory_id: str, user_id: str = Depends(get_user)):
    doc = get_store().get(memory_id, user_id)
    if not doc:
        raise HTTPException(404, "Memory not found")
    return doc


@router.put("/{memory_id}")
@limiter.limit("60/minute")
def update_memory(request: Request, memory_id: str, body: MemoryUpdate,
                  user_id: str = Depends(get_user)):
    updates = {}
    if body.content is not None:
        updates["content"] = body.content
        updates["embedding"] = embed(body.content)
    for field in ("category", "is_archived", "tags"):
        val = getattr(body, field)
        if val is not None:
            updates[field] = val
    if not updates:
        raise HTTPException(400, "No fields to update")
    if not get_store().update(memory_id, user_id, **updates):
        raise HTTPException(404, "Memory not found")
    return {"updated": True}


@router.delete("/{memory_id}")
@limiter.limit("30/minute")
def delete_memory(request: Request, memory_id: str, user_id: str = Depends(get_user)):
    if not get_store().delete(memory_id, user_id):
        raise HTTPException(404, "Memory not found")
    return {"deleted": True}


# ── Archive (soft-delete) ────────────────────────────
@router.patch("/{memory_id}/archive")
@limiter.limit("60/minute")
def archive_memory(request: Request, memory_id: str, user_id: str = Depends(get_user)):
    """归档记忆（软删除: 设置 is_archived=true）"""
    if not get_store().update(memory_id, user_id, is_archived=True):
        raise HTTPException(404, detail="Memory not found")
    return {"status": "archived", "memory_id": memory_id}

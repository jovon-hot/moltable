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
    persona_id: str | None = Field(default=None, description="关联的 Persona ID")


class MemoryUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=10000)
    category: str | None = Field(default=None, pattern=r"^(preference|decision|fact|project|insight|task|relationship)$")
    is_archived: bool | None = None
    tags: list[str] | None = Field(default=None, max_length=50)
    persona_id: str | None = Field(default=None)


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
        persona_id=body.persona_id,
    )
    return {"saved": True, "id": doc["id"]}


# ── Search ────────────────────────────────────────────
@router.get("/search")
@limiter.limit("120/minute")
def search_memory(request: Request, q: str = Query(..., min_length=1, max_length=500),
                  category: str | None = None, top_k: int = Query(default=5, ge=1, le=50),
                  user_id: str = Depends(get_user)):
    try:
        return _do_search(user_id, q, category, top_k)
    except Exception as e:
        # 兜底：任何错误都返回最近记忆，不崩溃
        recent = get_store().list(user_id, category=category, limit=top_k)
        return {
            "query": q,
            "results": [{
                "id": r["id"], "content": r["content"],
                "category": r["category"], "source": r["source"],
                "relevance": 0.5,
                "created_at": str(r.get("created_at", "")),
            } for r in recent],
            "fallback": True,
        }


def _do_search(user_id: str, q: str, category: str | None, top_k: int):
    vec = embed(q)
    results = get_store().search(user_id, vec, top_k=top_k, category=category)
    
    # 如果 pgvector 返回空，回退到关键词搜索（全文索引）
    if not results and not get_store()._offline:
        try:
            from app_state import supabase as sb
            # 先用 pg fulltext，失败/无结果则 ILIKE
            kw_resp = sb.rpc("match_memories_keyword", {
                "query_text": q,
                "match_user_id": user_id,
                "match_count": top_k,
                "match_category": category,
            }).execute()
            if kw_resp.data:
                results = [{
                    "id": str(r.get("id", "")),
                    "content": r.get("content", ""),
                    "category": r.get("category", ""),
                    "source": r.get("source", ""),
                    "relevance": float(r.get("rank", 0)),
                    "created_at": str(r.get("created_at", "")),
                } for r in kw_resp.data]
        except Exception:
            pass
        
        # 关键词搜索也返回空 → ILIKE 回退
        if not results:
            try:
                all_memories = get_store().list(user_id, category=category, limit=200)
                q_lower = q.lower()
                matches = []
                for m in all_memories:
                    content = m.get("content", "").lower()
                    if q_lower in content:
                        matches.append({
                            "id": m["id"], "content": m["content"],
                            "category": m["category"], "source": m["source"],
                            "relevance": 0.6,
                            "created_at": m.get("created_at", ""),
                        })
                results = matches[:top_k]
            except Exception:
                pass

    # 所有搜索策略都失败 → 返回最近记忆作为兜底
    if not results:
        recent = get_store().list(user_id, category=category, limit=top_k)
        results = [{
            "id": r["id"], "content": r["content"],
            "category": r["category"], "source": r["source"],
            "relevance": 0.5,
            "created_at": r.get("created_at", ""),
        } for r in recent]
    
    return {
        "query": q,
        "results": [{
            "id": r["id"], "content": r["content"],
            "category": r["category"], "source": r["source"],
            "relevance": r.get("relevance", r.get("similarity", 0)),
            "created_at": r.get("created_at", ""),
        } for r in results],
    }


# ── Stats ────────────────────────────────────────────
@router.get("/stats")
@limiter.limit("60/minute")
def memory_stats(request: Request, user_id: str = Depends(get_user)):
    """返回用户记忆统计（总数、归档数、按类别计数）"""
    try:
        store = get_store()
        st = store.stats(user_id)
        # 按类别统计
        by_category = {}
        all_memories = store.list(user_id, limit=10000)
        for m in all_memories:
            cat = m.get("category", "other")
            by_category[cat] = by_category.get(cat, 0) + 1
        return {
            "total": st.get("total", 0),
            "archived": st.get("archived", 0),
            "by_category": by_category,
        }
    except Exception:
        # 生产环境降级：直接查 Supabase count
        from app_state import supabase as sb
        total_resp = sb.table("memories").select("count", count="exact") \
            .eq("user_id", user_id).eq("is_archived", False).execute()
        archived_resp = sb.table("memories").select("count", count="exact") \
            .eq("user_id", user_id).eq("is_archived", True).execute()
        return {
            "total": total_resp.count if hasattr(total_resp, 'count') else 0,
            "archived": archived_resp.count if hasattr(archived_resp, 'count') else 0,
            "by_category": {},
        }


# ── CRUD ──────────────────────────────────────────────
@router.get("")
@limiter.limit("120/minute")
def list_memories(request: Request, category: str | None = None,
                  persona_id: str | None = None,
                  limit: int = Query(default=50, ge=1, le=200),
                  offset: int = Query(default=0, ge=0),
                  user_id: str = Depends(get_user)):
    all_memories = get_store().list(user_id, category=category, limit=10000)
    # 应用 persona_id 过滤
    if persona_id:
        all_memories = [m for m in all_memories if str(m.get("persona_id","")) == persona_id]
    # 分页
    results = all_memories[offset:offset+limit]
    return {
        "memories": results,
        "total": len(all_memories),
        "limit": limit,
        "offset": offset,
    }


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
    for field in ("category", "is_archived", "tags", "persona_id"):
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

from __future__ import annotations
"""Memory routes — CRUD + semantic search with in-memory vector store"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from app_state import limiter, get_store
from routes.auth import get_user
from services.embedding import embed

router = APIRouter(prefix="/api/memories", tags=["memories"])


# ── Time-decay helper ──────────────────────────────────────
def _apply_time_decay(results: list[dict]) -> list[dict]:
    """Boost recency: blend semantic similarity with time decay.
    
    Uses exponential decay with half-life of 7 days. Newer memories get
    a slight boost in relevance score. Result is still primarily ranked
    by similarity, but with recent items slightly favored.
    
    Inspired by: Zep temporal knowledge graph, OpenAI memory recency weighting.
    """
    import math, time as _time_module
    now = _time_module.time()
    HALF_LIFE_SECONDS = 7 * 24 * 3600  # 7 days
    
    for r in results:
        created_str = r.get("created_at", "")
        age_seconds = float(HALF_LIFE_SECONDS)  # default: max age
        if created_str:
            try:
                # Parse ISO timestamp
                from datetime import datetime
                dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                age_seconds = max(0, now - dt.timestamp())
            except Exception:
                pass
        
        # Decay factor: 1.0 for now, 0.5 for half-life, approaches 0 for very old
        decay = math.exp(-math.log(2) * age_seconds / HALF_LIFE_SECONDS)
        # Blend: 80% similarity + 20% time boost
        base_relevance = r.get("relevance", r.get("similarity", 0.5))
        r["relevance"] = round(0.8 * base_relevance + 0.2 * decay, 4)
        r["time_boost"] = round(decay, 4)
    
    # Re-sort by blended relevance
    results.sort(key=lambda r: r.get("relevance", 0), reverse=True)
    return results


class MemoryCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Memory content")
    category: str = Field(default="fact", pattern=r"^(preference|decision|fact|project|insight|task|relationship)$")
    source: str | None = Field(default=None, max_length=200, description="来源（hermes/claude/chatgpt/manual/agent）。未传时从 X-Agent-Platform 请求头推断，仍无则记 unknown")
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

    # source 解析: 显式传参 → X-Agent-Platform 请求头 → unknown
    agent_platform = (request.headers.get("x-agent-platform") or "").strip()
    source = ((body.source or "").strip() or agent_platform or "unknown")[:200]

    doc = get_store().insert(
        user_id, body.content, vec,
        category=body.category, source=source,
        confidence=body.confidence, tags=body.tags,
        persona_id=body.persona_id,
    )
    return {"saved": True, "id": doc["id"], "source": source}


# ── Search ────────────────────────────────────────────
@router.get("/search")
@limiter.limit("120/minute")
def search_memory(request: Request, q: str = Query(..., min_length=1, max_length=500),
                  category: str | None = None, top_k: int = Query(default=5, ge=1, le=50),
                  time_decay: bool = Query(default=False, description="Boost recent memories in rankings"),
                  user_id: str = Depends(get_user)):
    try:
        results = _do_search(user_id, q, category, top_k)
        if time_decay and results.get("results"):
            results["results"] = _apply_time_decay(results["results"])
        return results
    except Exception as e:
        # 兜底：任何错误都返回最近记忆，不崩溃
        recent = get_store().list(user_id, category=category, limit=top_k)
        return {
            "query": q,
            "results": [{
                "id": r["id"], "content": r["content"],
                "category": r["category"], "source": r["source"],
                "tags": r.get("tags") or [],
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
                    "tags": r.get("tags") or [],
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
                            "tags": m.get("tags") or [],
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
            "tags": r.get("tags") or [],
            "relevance": 0.5,
            "created_at": r.get("created_at", ""),
        } for r in recent]
    
    return {
        "query": q,
        "results": [{
            "id": r["id"], "content": r["content"],
            "category": r["category"], "source": r["source"],
            "tags": r.get("tags") or [],
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


# ── Duplicate Detection ────────────────────────────
class DuplicateGroup(BaseModel):
    representative: dict
    duplicates: list[dict]
    count: int
    avg_similarity: float

@router.get("/duplicates")
@limiter.limit("30/minute")
def find_duplicates(
    request: Request,
    threshold: float = Query(default=0.85, ge=0.7, le=0.99),
    user_id: str = Depends(get_user),
):
    """Find clusters of near-duplicate memories for consolidation.

    Uses cosine similarity on embeddings to find memory groups where
    pairwise similarity exceeds the threshold. Returns groups sorted by
    count descending (most duplicated first).

    Inspired by: OpenAI Dreaming V3 memory synthesis, Cognee session distillation.
    """
    store = get_store()
    all_memories = store.list(user_id, limit=500)

    if len(all_memories) < 2:
        return {"groups": [], "total_memories": len(all_memories)}

    # Build group index: group_id -> list of memory dicts
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

            if sim >= threshold:
                group.append(b)
                used.add(b["id"])

        if len(group) >= 2:
            groups.append(group)

    # Sort by group size descending
    groups.sort(key=lambda g: len(g), reverse=True)

    result_groups = []
    for group in groups:
        # Pick the most recent as representative
        rep = max(group, key=lambda m: m.get("created_at", ""))
        dups = [m for m in group if m["id"] != rep["id"]]
        similarities = []
        try:
            from repositories.memory_repo import _cosine_sim
            rep_emb = rep.get("embedding") or []
            for d in dups:
                d_emb = d.get("embedding") or []
                if rep_emb and d_emb:
                    similarities.append(_cosine_sim(rep_emb, d_emb))
        except Exception:
            pass
        avg_sim = round(sum(similarities) / len(similarities), 3) if similarities else 0.0

        result_groups.append({
            "representative": {
                "id": rep["id"],
                "content": rep["content"][:200],
                "category": rep.get("category", ""),
                "created_at": rep.get("created_at", ""),
                "source": rep.get("source", ""),
            },
            "duplicates": [{
                "id": m["id"],
                "content": m["content"][:200],
                "category": m.get("category", ""),
                "created_at": m.get("created_at", ""),
            } for m in dups],
            "count": len(group),
            "avg_similarity": avg_sim,
        })

    return {
        "groups": result_groups[:20],
        "total_memories": len(all_memories),
        "threshold": threshold,
    }


# ── Memory Consolidation ───────────────────────────
class ConsolidateRequest(BaseModel):
    memory_ids: list[str] = Field(..., min_length=2, max_length=20, description="Memory IDs to consolidate")
    strategy: str = Field(default="merge", pattern=r"^(merge|summarize|deduplicate)$",
                         description="merge=blend into one, summarize=extract key insight, deduplicate=keep best")

@router.post("/consolidate")
@limiter.limit("10/minute")
def consolidate_memories(request: Request, body: ConsolidateRequest,
                         user_id: str = Depends(get_user)):
    """Consolidate multiple related memories into one synthesized memory.

    Uses DeepSeek LLM to intelligently merge/summarize related memories.
    The result is stored as a new memory (category='insight' for summarize,
    category='fact' for merge/deduplicate).

    Original memories are archived after successful consolidation.

    Inspired by: OpenAI Dreaming V3 (background memory synthesis),
    Cognee session distillation, Zep temporal knowledge graph.
    """
    store = get_store()

    # Fetch all memories and verify ownership
    memories = []
    for mid in body.memory_ids:
        mem = store.get(mid, user_id)
        if not mem:
            raise HTTPException(404, f"Memory {mid} not found")
        memories.append(mem)

    if len(memories) < 2:
        raise HTTPException(400, "Need at least 2 memories to consolidate")

    # Prepare LLM prompt
    import logging
    logger_local = logging.getLogger("moltable.consolidate")

    memory_texts = "\n\n---\n\n".join([
        f"[Memory {i+1}] ({m['category']}, {m.get('source','unknown')})\n{m['content']}"
        for i, m in enumerate(memories)
    ])

    strategy_prompts = {
        "merge": (
            "You are a memory consolidation engine. Below are several related memories "
            "from the same user. Merge them into ONE coherent, non-redundant memory that "
            "preserves all unique facts while eliminating repetition. "
            "Respond with ONLY the consolidated memory text — no JSON, no explanation.\n\n"
        ),
        "summarize": (
            "You are a memory synthesis engine. Below are several related memories from the "
            "same user. Extract the KEY INSIGHT or pattern that emerges across all of them. "
            "Respond with ONLY the insight text (1-3 sentences) — no JSON, no explanation.\n\n"
        ),
        "deduplicate": (
            "You are a memory deduplication engine. Below are several related memories from the "
            "same user that likely say the same thing in different ways. Pick the BEST, clearest "
            "version of the fact and return ONLY that text. Do not add new information.\n\n"
        ),
    }

    prompt = strategy_prompts.get(body.strategy, strategy_prompts["merge"]) + memory_texts

    # Use DeepSeek for consolidation
    from app_state import supabase as _sb_check
    deepseek_key = __import__("os").getenv("DEEPSEEK_API_KEY")
    consolidated_text = None

    if deepseek_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com/v1")

            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )
            consolidated_text = resp.choices[0].message.content.strip()
            if not consolidated_text:
                raise ValueError("Empty response from LLM")
            logger_local.info("Consolidated %d memories (strategy=%s)", len(memories), body.strategy)
        except Exception as e:
            logger_local.warning("DeepSeek consolidation failed: %s — using fallback", e)
            consolidated_text = None

    if not consolidated_text:
        # Fallback: pick the longest memory content as the base
        longest = max(memories, key=lambda m: len(m["content"]))
        sources = [m.get("source", "unknown")[:50] for m in memories]
        consolidated_text = (
            f"[Consolidated from {len(memories)} related memories]\n\n"
            f"{longest['content']}\n\n"
            f"--- Additional context merged ---\n"
            + "\n".join([f"• {m['content'][:200]}" for m in memories if m['id'] != longest['id']])
        )

    # Determine category and source
    category_map = {"summarize": "insight", "merge": "fact", "deduplicate": "fact"}
    new_category = category_map.get(body.strategy, "fact")
    sources = list(set(m.get("source", "unknown")[:30] for m in memories))
    new_source = "+".join(sources[:3]) if sources else "consolidated"

    # Combine tags
    all_tags: list[str] = []
    for m in memories:
        for t in (m.get("tags") or []):
            if t not in all_tags:
                all_tags.append(t)

    # Create consolidated memory
    from services.embedding import embed as embed_fn
    new_vec = embed_fn(consolidated_text)

    new_doc = store.insert(
        user_id, consolidated_text, new_vec,
        category=new_category,
        source=f"consolidated:{new_source}",
        confidence=0.9,
        tags=all_tags[:20],
        persona_id=memories[0].get("persona_id"),
    )

    # Archive original memories
    archived_count = 0
    for m in memories:
        try:
            store.update(m["id"], user_id, is_archived=True)
            archived_count += 1
        except Exception:
            pass

    return {
        "consolidated": {
            "id": new_doc["id"],
            "content": consolidated_text,
            "category": new_category,
            "source": new_source,
        },
        "archived_count": archived_count,
        "original_count": len(memories),
        "strategy": body.strategy,
    }

from __future__ import annotations

"""Knowledge graph routes — entity/relationship graph over user memories."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app_state import get_store, limiter
from routes.auth import get_user
from services.knowledge_graph import knowledge_graph_service

logger = logging.getLogger("moltable.knowledge")

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


# ── Full graph ─────────────────────────────────────────
@router.get("/graph")
@limiter.limit("60/minute")
def get_knowledge_graph(
    request: Request,
    min_weight: int = Query(default=1, ge=1, le=100,
                            description="Only include edges with weight >= min_weight"),
    limit: int = Query(default=200, ge=1, le=2000,
                       description="Max nodes to return (top by memory count)"),
    user_id: str = Depends(get_user),
):
    """Return the user's full knowledge graph (nodes + weighted edges)."""
    return knowledge_graph_service.get_graph(user_id, min_weight=min_weight, limit=limit)


# ── Single entity + connections ────────────────────────
@router.get("/entity")
@limiter.limit("120/minute")
def get_entity(
    request: Request,
    name: str = Query(..., min_length=1, max_length=200,
                      description="Entity name to look up"),
    user_id: str = Depends(get_user),
):
    """Entity details plus all its connections (neighbors, weights, relations)."""
    result = knowledge_graph_service.find_entity_connections(user_id, name)
    if result is None:
        raise HTTPException(404, f"Entity '{name}' not found in knowledge graph")
    return result


# ── Path between two entities ──────────────────────────
@router.get("/path")
@limiter.limit("60/minute")
def find_path(
    request: Request,
    source: str = Query(..., min_length=1, max_length=200),
    target: str = Query(..., min_length=1, max_length=200),
    user_id: str = Depends(get_user),
):
    """Shortest path between two entities through the knowledge graph."""
    result = knowledge_graph_service.find_path(user_id, source, target)
    if result is None:
        raise HTTPException(404, f"No path between '{source}' and '{target}'")
    return result


# ── Related entities (helper, used by entity lookup clients) ──
@router.get("/related")
@limiter.limit("120/minute")
def related_entities(
    request: Request,
    name: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(default=10, ge=1, le=50),
    user_id: str = Depends(get_user),
):
    """Entities related to `name`, ranked by co-occurrence weight."""
    return {
        "entity": name,
        "related": knowledge_graph_service.find_related_entities(user_id, name, limit=limit),
    }


# ── Rebuild from existing memories ─────────────────────
@router.post("/build")
@limiter.limit("10/minute")
def rebuild_graph(request: Request, user_id: str = Depends(get_user)):
    """Rebuild the knowledge graph from all of the user's existing memories."""
    memories = get_store().list(user_id, limit=10000)
    stats = knowledge_graph_service.rebuild(user_id, memories)
    logger.info("KG rebuild user=%s memories=%d nodes=%d edges=%d",
                user_id, stats.get("added", 0), stats.get("nodes", 0), stats.get("edges", 0))
    return {
        "status": "built",
        "memories_processed": stats.get("added", 0),
        "nodes": stats.get("nodes", 0),
        "edges": stats.get("edges", 0),
    }

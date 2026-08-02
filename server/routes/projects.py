"""Project routes — manage project environments with knowledge_bases and tools."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from app_state import supabase, limiter
from routes.auth import get_user
from datetime import datetime, timezone

router = APIRouter(prefix="/api/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    persona_id: Optional[str] = None
    knowledge_bases: list = Field(default=[])
    tools: list = Field(default=[])
    is_active: bool = True


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    persona_id: Optional[str] = None
    knowledge_bases: Optional[list] = None
    tools: Optional[list] = None
    is_active: Optional[bool] = None


@router.get("")
@limiter.limit("60/minute")
def list_projects(request: Request, user_id: str = Depends(get_user)):
    resp = supabase.table("projects") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .execute()
    return {
        "projects": [_clean_project(r) for r in (resp.data or [])]
    }


@router.get("/{project_id}")
@limiter.limit("60/minute")
def get_project(project_id: str, request: Request, user_id: str = Depends(get_user)):
    resp = supabase.table("projects") \
        .select("*") \
        .eq("id", project_id) \
        .eq("user_id", user_id) \
        .single() \
        .execute()
    if not resp.data:
        raise HTTPException(404, "项目不存在")
    return _clean_project(resp.data)


@router.post("")
@limiter.limit("30/hour")
def create_project(body: ProjectCreate, request: Request, user_id: str = Depends(get_user)):
    import uuid
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": body.name,
        "description": body.description,
        "knowledge_bases": body.knowledge_bases,
        "tools": body.tools,
        "is_active": body.is_active,
        "created_at": now,
        "updated_at": now,
    }
    if body.persona_id:
        row["persona_id"] = body.persona_id

    supabase.table("projects").insert(row).execute()
    return _clean_project(row)


@router.patch("/{project_id}")
@limiter.limit("30/hour")
def update_project(project_id: str, body: ProjectUpdate, request: Request, user_id: str = Depends(get_user)):
    # Verify ownership
    existing = supabase.table("projects") \
        .select("id") \
        .eq("id", project_id) \
        .eq("user_id", user_id) \
        .single() \
        .execute()
    if not existing.data:
        raise HTTPException(404, "项目不存在")

    payload = {}
    for field in ["name", "description", "persona_id", "knowledge_bases", "tools", "is_active"]:
        val = getattr(body, field, None)
        if val is not None:
            payload[field] = val
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()

    supabase.table("projects").update(payload).eq("id", project_id).execute()

    resp = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    return _clean_project(resp.data)


def _clean_project(row: dict) -> dict:
    return {
        "id": row.get("id", ""),
        "name": row.get("name", ""),
        "description": row.get("description", ""),
        "persona_id": row.get("persona_id"),
        "knowledge_bases": row.get("knowledge_bases") or [],
        "tools": row.get("tools") or [],
        "is_active": row.get("is_active", True),
        "created_at": str(row.get("created_at", "")),
        "updated_at": str(row.get("updated_at", "")),
    }

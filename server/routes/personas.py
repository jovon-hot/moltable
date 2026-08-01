from __future__ import annotations
"""
Persona routes — 人格管理 (Phase 2)
支持 Supabase 持久化 + In-memory fallback (offline 模式)
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from app_state import supabase, limiter
from app_state import bump_persona_version, _is_sqlite
from routes.auth import get_user
from services.persona_store import get_persona_store

router = APIRouter(prefix="/api/personas", tags=["personas"])


class PersonaCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    type: str = Field(default="constructed", max_length=100)
    description: str = Field(default="", max_length=2000)
    system_prompt: str = Field(default="", max_length=10000)
    traits: dict = Field(default={})
    model_preference: str | None = Field(default=None, max_length=200)


class PersonaUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    type: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    system_prompt: str | None = Field(default=None, max_length=10000)
    traits: dict | None = Field(default=None)
    model_preference: str | None = Field(default=None, max_length=200)


# ── Helpers ──────────────────────────────────────────

def _is_offline() -> bool:
    """SQLite模式不经过supabase表 — Persona走内存存储"""
    return supabase is None or _is_sqlite


def _list_personas(user_id: str) -> list:
    """List active personas — Supabase → in-memory fallback."""
    if not _is_offline():
        try:
            return (
                supabase.table("personas")
                .select("*")
                .eq("user_id", user_id)
                .eq("is_active", True)
                .execute()
                .data
            )
        except Exception:
            pass  # fall through to in-memory
    return get_persona_store().list(user_id)


def _list_own_personas(user_id: str) -> list:
    """仅返回用户自己创建的 Persona（不含 demo）—— 用于配额计算"""
    pstore = get_persona_store()
    return [p for p in pstore.list(user_id) if p.get("user_id") == user_id]


def _get_persona(persona_id: str, user_id: str) -> dict | None:
    """Get single persona — Supabase → in-memory fallback."""
    if not _is_offline():
        try:
            result = (
                supabase.table("personas")
                .select("*")
                .eq("id", persona_id)
                .eq("user_id", user_id)
                .eq("is_active", True)
                .execute()
            )
            if result.data:
                return result.data[0]
        except Exception:
            pass
    return get_persona_store().get(persona_id, user_id)


def _create_persona(user_id: str, data: dict) -> dict:
    """Create persona — Supabase → in-memory fallback."""
    from services.quota import check_quota
    # 检查配额（不计demo personas）
    current = len(_list_own_personas(user_id))
    check_quota(user_id, "personas", current)

    if not _is_offline():
        try:
            result = (
                supabase.table("personas")
                .insert({
                    "user_id": user_id,
                    "name": data["name"],
                    "type": data.get("type", "constructed"),
                    "description": data.get("description", ""),
                    "system_prompt": data.get("system_prompt", ""),
                    "traits": data.get("traits", {}),
                    "model_preference": data.get("model_preference"),
                })
                .execute()
            )
            bump_persona_version()
            return {"created": True, "id": result.data[0]["id"]}
        except Exception:
            pass
    # In-memory fallback
    p = get_persona_store().create(user_id, data)
    bump_persona_version()
    return {"created": True, "id": p["id"]}


def _update_persona(persona_id: str, user_id: str, data: dict) -> bool:
    """Update persona — Supabase → in-memory fallback."""
    bump_persona_version()
    if not _is_offline():
        try:
            supabase.table("personas") \
                .update(data) \
                .eq("id", persona_id) \
                .eq("user_id", user_id) \
                .execute()
            return True
        except Exception:
            pass
    return get_persona_store().update(persona_id, user_id, data)


def _delete_persona(persona_id: str, user_id: str) -> bool:
    """Soft-delete persona — Supabase → in-memory fallback."""
    bump_persona_version()
    if not _is_offline():
        try:
            supabase.table("personas") \
                .update({"is_active": False}) \
                .eq("id", persona_id) \
                .eq("user_id", user_id) \
                .execute()
            return True
        except Exception:
            pass
    return get_persona_store().delete(persona_id, user_id)


# ── Routes ──────────────────────────────────────────

@router.get("")
@limiter.limit("120/minute")
def list_personas(request: Request, user_id: str = Depends(get_user)):
    personas = _list_personas(user_id)
    # 为每个 persona 计算关联的记忆数
    try:
        from app_state import supabase as sb
        for p in personas:
            cnt = sb.table("memories").select("count", count="exact") \
                .eq("persona_id", p["id"]).execute()
            p["memory_count"] = cnt.count if hasattr(cnt, 'count') else 0
    except Exception:
        for p in personas:
            p.setdefault("memory_count", 0)
    return personas


@router.get("/{persona_id}")
@limiter.limit("120/minute")
def get_persona(request: Request, persona_id: str, user_id: str = Depends(get_user)):
    result = _get_persona(persona_id, user_id)
    if not result:
        return JSONResponse(status_code=404, content={"detail": "Persona not found"})
    return result


@router.post("")
@limiter.limit("30/hour")
def create_persona(request: Request, body: PersonaCreate, user_id: str = Depends(get_user)):
    return _create_persona(user_id, body.model_dump())


@router.put("/{persona_id}")
@limiter.limit("60/minute")
def update_persona(request: Request, persona_id: str, body: PersonaUpdate,
                   user_id: str = Depends(get_user)):
    existing = _get_persona(persona_id, user_id)
    if not existing:
        return JSONResponse(status_code=404, content={"detail": "Persona not found"})

    update_payload = {}
    for field in ("name", "type", "description", "system_prompt", "traits", "model_preference"):
        value = getattr(body, field, None)
        if value is not None:
            update_payload[field] = value

    if not update_payload:
        return JSONResponse(status_code=400, content={"detail": "No fields to update"})

    _update_persona(persona_id, user_id, update_payload)
    return {"updated": True, "id": persona_id}


@router.delete("/{persona_id}")
@limiter.limit("30/minute")
def delete_persona(request: Request, persona_id: str, user_id: str = Depends(get_user)):
    existing = _get_persona(persona_id, user_id)
    if not existing:
        return JSONResponse(status_code=404, content={"detail": "Persona not found"})

    _delete_persona(persona_id, user_id)
    return {"deleted": True, "id": persona_id}

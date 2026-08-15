"""Git-style bidirectional sync REST endpoints.

- POST /api/sync/push    — push local changes; conflicts reported, never overwritten
- POST /api/sync/pull    — pull server changes since a timestamp
- POST /api/sync/resolve — accept a client-resolved conflict with a version bump
- POST /api/sync/export  — download all user data as JSON
- POST /api/sync/import  — upload and merge a JSON export
"""

from typing import Any, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app_state import supabase
from routes.auth import get_user
from services.sync_service import SyncService

router = APIRouter(prefix="/api/sync", tags=["sync"])

ITEM_TYPES = (
    ("memory", "memories"),
    ("persona", "personas"),
    ("project", "projects"),
    ("decision", "decisions"),
    ("did", "dids"),
    ("credential", "credentials"),
    ("persona_version", "persona_versions"),
    ("profile", "profiles"),
)


class SyncItem(BaseModel):
    id: str
    content: Any
    base_version: int = Field(default=0, ge=0)
    updated_at: Optional[str] = None


class PushRequest(BaseModel):
    memories: List[SyncItem] = Field(default_factory=list)
    personas: List[SyncItem] = Field(default_factory=list)
    projects: List[SyncItem] = Field(default_factory=list)
    decisions: List[SyncItem] = Field(default_factory=list)
    dids: List[SyncItem] = Field(default_factory=list)
    credentials: List[SyncItem] = Field(default_factory=list)
    persona_versions: List[SyncItem] = Field(default_factory=list)
    profiles: List[SyncItem] = Field(default_factory=list)


class PullRequest(BaseModel):
    since: Optional[str] = None


class ResolveRequest(BaseModel):
    id: str
    type: Literal["memory", "persona", "project", "decision"]
    resolved_content: Any
    base_version: int = Field(default=0, ge=0)


@router.post("/push")
def push(payload: PushRequest, user_id: str = Depends(get_user)):
    """Push local changes. Conflicting rows are returned for resolution."""
    service = SyncService(supabase, user_id)
    accepted: List[dict] = []
    conflicts: List[dict] = []
    for item_type, field in ITEM_TYPES:
        result = service.push([item.model_dump() for item in getattr(payload, field)], item_type)
        accepted.extend(result["accepted"])
        conflicts.extend(result["conflicts"])
    return {"accepted": accepted, "conflicts": conflicts}


@router.post("/pull")
def pull(payload: PullRequest, user_id: str = Depends(get_user)):
    """Pull server changes since a timestamp (empty since -> everything)."""
    return SyncService(supabase, user_id).pull(payload.since)


@router.post("/resolve")
def resolve(payload: ResolveRequest, user_id: str = Depends(get_user)):
    """Accept a client-resolved conflict; the server bumps the version."""
    try:
        return SyncService(supabase, user_id).resolve(
            payload.id, payload.type, payload.resolved_content, payload.base_version
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/export")
def export_data(user_id: str = Depends(get_user)):
    """Download all user data as a JSON object."""
    return SyncService(supabase, user_id).export_all()


@router.post("/import")
def import_data(payload: dict, user_id: str = Depends(get_user)):
    """Upload and merge a JSON export payload."""
    return SyncService(supabase, user_id).import_data(payload)

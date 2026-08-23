"""File-level backup sync REST endpoints.

- POST /api/backup/sources        — create a backup source
- GET  /api/backup/sources        — list user's backup sources
- POST /api/backup/push           — push a new snapshot (manifest + changed blobs)
- POST /api/backup/pull           — pull a snapshot (manifest + blob contents)
- POST /api/backup/manifest       — get latest manifest only (for client diff)
"""

from __future__ import annotations

import base64
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app_state import limiter, supabase
from routes.auth import get_user
from services.backup_service import BackupService, StorageQuotaExceeded

router = APIRouter(prefix="/api/backup", tags=["backup"])


class CreateSourceRequest(BaseModel):
    agent_type: str
    name: str


class PushRequest(BaseModel):
    source_id: str
    manifest: Dict[str, str] = Field(default_factory=dict)
    # blobs: hash -> base64(content)。客户端只传「变化」的文件内容。
    blobs: Dict[str, str] = Field(default_factory=dict)


class PullRequest(BaseModel):
    source_id: str
    version: Optional[int] = None


class ManifestRequest(BaseModel):
    source_id: str
    version: Optional[int] = None


@router.post("/sources")
@limiter.limit("20/hour")
def create_source(request: Request, body: CreateSourceRequest, user_id: str = Depends(get_user)):
    if not body.agent_type.strip() or not body.name.strip():
        raise HTTPException(status_code=400, detail="agent_type and name are required")

    # 备份源数量配额检查
    from services.quota import _get_user_plan
    from pricing_config import build_plan

    plan = _get_user_plan(user_id)
    max_sources = build_plan(plan)["limits"]["backup_sources"]
    if max_sources >= 0:  # -1 = 无限
        current = len(BackupService(supabase, user_id).list_sources())
        if current >= max_sources:
            raise HTTPException(
                status_code=402,
                detail=f"备份源数量已达 {max_sources} 上限。升级 Pro 解锁更多。",
            )

    return BackupService(supabase, user_id).create_source(body.agent_type.strip(), body.name.strip())


@router.get("/sources")
@limiter.limit("120/minute")
def list_sources(request: Request, user_id: str = Depends(get_user)):
    return {"sources": BackupService(supabase, user_id).list_sources()}


@router.get("/sources/{source_id}")
@limiter.limit("120/minute")
def get_source_detail(request: Request, source_id: str, user_id: str = Depends(get_user)):
    """备份源详情：基本信息 + 版本历史。"""
    svc = BackupService(supabase, user_id)
    try:
        source = svc._get_source(source_id)
    except Exception:
        source = None
    if source is None:
        raise HTTPException(status_code=404, detail="source not found or not owned by user")
    snapshots = svc.list_snapshots(source_id)
    return {
        "id": source.get("id"),
        "agent_type": source.get("agent_type"),
        "name": source.get("name"),
        "latest_version": source.get("latest_version"),
        "created_at": source.get("created_at"),
        "snapshots": snapshots,
    }


@router.delete("/sources/{source_id}")
@limiter.limit("20/hour")
def delete_source(request: Request, source_id: str, user_id: str = Depends(get_user)):
    """删除备份源及其所有快照（不可恢复）。"""
    try:
        BackupService(supabase, user_id).delete_source(source_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"deleted": True, "source_id": source_id}


@router.post("/push")
@limiter.limit("20/hour")
def push(request: Request, body: PushRequest, user_id: str = Depends(get_user)):
    blobs: Dict[str, bytes] = {}
    for h, b64 in body.blobs.items():
        try:
            blobs[h] = base64.b64decode(b64)
        except Exception:
            raise HTTPException(status_code=400, detail=f"invalid base64 for blob {h}")
    try:
        result = BackupService(supabase, user_id).push(body.source_id, body.manifest, blobs)
    except StorageQuotaExceeded as exc:
        raise HTTPException(status_code=402, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"version": result.version, "stored_blobs": result.stored_blobs, "skipped_blobs": result.skipped_blobs}


@router.post("/pull")
@limiter.limit("30/minute")
def pull(request: Request, body: PullRequest, user_id: str = Depends(get_user)):
    try:
        result = BackupService(supabase, user_id).pull(body.source_id, body.version)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    # blobs 转 base64 返回
    result["blobs"] = {h: base64.b64encode(d).decode() for h, d in result["blobs"].items()}
    return result


@router.post("/manifest")
@limiter.limit("60/minute")
def get_manifest(request: Request, body: ManifestRequest, user_id: str = Depends(get_user)):
    try:
        return BackupService(supabase, user_id).get_manifest(body.source_id, body.version)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

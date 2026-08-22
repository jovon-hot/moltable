"""File-level backup sync — 周期性快照 + CAS 内容寻址.

与 sync_service.py（结构化记忆条目同步）并行，本服务做「灵魂资产文件打包备份」：
- backup_sources: 每个 agent 框架实例一个备份源
- snapshots: 每个快照 = 一份 manifest（path -> content hash）
- blob 内容存对象存储（Supabase Storage），按 hash 寻址去重

核心边界（见设计文档 v0.3）：只备份「灵魂资产」（记忆文件 + 导出的记忆 JSON），
不备份「流水账」（对话日志 db / FTS 索引）。
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

TABLE_SOURCES = "backup_sources"
TABLE_SNAPSHOTS = "snapshots"
BACKUP_BUCKET = "agent-backups"


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


# ── Blob 存储抽象 ──────────────────────────────────────────


class BlobStore:
    """对象存储抽象：put/get/exists。生产 = Supabase Storage，测试 = 内存 dict。"""

    def put(self, key: str, data: bytes) -> None:
        raise NotImplementedError

    def get(self, key: str) -> Optional[bytes]:
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        raise NotImplementedError


class MemoryBlobStore(BlobStore):
    """测试用内存存储。"""

    def __init__(self):
        self._data: Dict[str, bytes] = {}

    def put(self, key: str, data: bytes) -> None:
        self._data[key] = data

    def get(self, key: str) -> Optional[bytes]:
        return self._data.get(key)

    def exists(self, key: str) -> bool:
        return key in self._data


class FileSystemBlobStore(BlobStore):
    """本地文件系统存储（SQLite 模式 / 本地开发）。blob 按 hash 存到磁盘目录。"""

    def __init__(self, base_dir: str):
        self._base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def _path(self, key: str) -> str:
        return os.path.join(self._base_dir, key.replace("/", "_"))

    def put(self, key: str, data: bytes) -> None:
        with open(self._path(key), "wb") as f:
            f.write(data)

    def get(self, key: str) -> Optional[bytes]:
        try:
            with open(self._path(key), "rb") as f:
                return f.read()
        except (OSError, FileNotFoundError):
            return None

    def exists(self, key: str) -> bool:
        return os.path.exists(self._path(key))


class SupabaseBlobStore(BlobStore):
    """Supabase Storage 实现：key = {user_id}/{hash}。"""

    def __init__(self, supabase_client, user_id: str):
        self._client = supabase_client
        self._user_id = user_id

    def _key(self, key: str) -> str:
        return f"{self._user_id}/{key}"

    def put(self, key: str, data: bytes) -> None:
        self._client.storage.from_(BACKUP_BUCKET).upload(
            self._key(key), data,
            {"content-type": "application/octet-stream"},
        )

    def get(self, key: str) -> Optional[bytes]:
        try:
            return self._client.storage.from_(BACKUP_BUCKET).download(self._key(key))
        except Exception:
            return None

    def exists(self, key: str) -> bool:
        try:
            res = self._client.storage.from_(BACKUP_BUCKET).list(self._key(key))
            return bool(res)
        except Exception:
            return False


# ── 备份源服务 ──────────────────────────────────────────────


@dataclass
class PushResult:
    version: int
    stored_blobs: int
    skipped_blobs: int


class BackupService:
    """Per-user backup operations against a Supabase-compatible client."""

    def __init__(self, db, user_id: str, blob_store: Optional[BlobStore] = None):
        self.db = db
        self.user_id = user_id
        self._blob_store = blob_store

    # ── blob store 惰性初始化（生产 Supabase Storage，测试注入内存）──

    def _store(self) -> BlobStore:
        if self._blob_store is None:
            from app_state import _is_sqlite
            if _is_sqlite:
                # SQLite 本地模式：blob 持久化到磁盘（DB 同目录 blobs/）
                from repositories.sqlite_adapter import DB_PATH
                base_dir = os.path.join(os.path.dirname(DB_PATH), "backup_blobs")
                self._blob_store = FileSystemBlobStore(base_dir)
            else:
                from app_state import supabase as _supabase
                self._blob_store = SupabaseBlobStore(_supabase, self.user_id)
        return self._blob_store

    # ── 备份源管理 ──────────────────────────────────────────

    def create_source(self, agent_type: str, name: str) -> dict:
        source_id = str(uuid.uuid4())
        row = {
            "id": source_id,
            "user_id": self.user_id,
            "agent_type": agent_type,
            "name": name,
            "latest_version": 0,
            "created_at": utcnow(),
        }
        self.db.table(TABLE_SOURCES).insert(row).execute()
        return {"id": source_id, "agent_type": agent_type, "name": name, "latest_version": 0}

    def list_sources(self) -> list:
        try:
            rows = (
                self.db.table(TABLE_SOURCES)
                .select("*")
                .eq("user_id", self.user_id)
                .order("created_at")
                .execute()
                .data
            )
        except Exception:
            rows = []
        return rows or []

    def _get_source(self, source_id: str) -> Optional[dict]:
        rows = (
            self.db.table(TABLE_SOURCES)
            .select("*")
            .eq("id", source_id)
            .eq("user_id", self.user_id)
            .limit(1)
            .execute()
            .data
        )
        return rows[0] if rows else None

    def _get_snapshot(self, source_id: str, version: int) -> Optional[dict]:
        rows = (
            self.db.table(TABLE_SNAPSHOTS)
            .select("*")
            .eq("source_id", source_id)
            .eq("version", version)
            .limit(1)
            .execute()
            .data
        )
        return rows[0] if rows else None

    # ── push：上传增量快照 ──────────────────────────────────

    def push(self, source_id: str, manifest: Dict[str, str], blobs: Dict[str, bytes]) -> PushResult:
        """Push a new snapshot.

        manifest: {path: hash}，hash 形如 "sha256:..."
        blobs: {hash: bytes}，只含客户端判定为「变化」的文件内容（已存在则服务端跳过）
        """
        source = self._get_source(source_id)
        if source is None:
            raise ValueError(f"source {source_id} not found or not owned by user")

        latest = int(source.get("latest_version") or 0)
        next_version = latest + 1
        store = self._store()

        stored = 0
        skipped = 0
        for h, data in blobs.items():
            if not h.startswith("sha256:"):
                continue
            # 内容寻址去重：hash 相同即复用，不重复上传
            if store.exists(h):
                skipped += 1
                continue
            store.put(h, data)
            stored += 1

        snapshot_row = {
            "id": str(uuid.uuid4()),
            "source_id": source_id,
            "version": next_version,
            "manifest": manifest,  # dict → jsonb
            "parent_version": latest if latest > 0 else None,
            "created_at": utcnow(),
        }
        self.db.table(TABLE_SNAPSHOTS).insert(snapshot_row).execute()

        self.db.table(TABLE_SOURCES).update({"latest_version": next_version}) \
            .eq("id", source_id).eq("user_id", self.user_id).execute()

        return PushResult(version=next_version, stored_blobs=stored, skipped_blobs=skipped)

    # ── pull：下载快照 ──────────────────────────────────────

    def pull(self, source_id: str, version: Optional[int] = None) -> dict:
        """Return manifest + blob contents for a snapshot (default latest)."""
        source = self._get_source(source_id)
        if source is None:
            raise ValueError(f"source {source_id} not found or not owned by user")

        target = version if version is not None else int(source.get("latest_version") or 0)
        if target <= 0:
            return {"version": 0, "manifest": {}, "blobs": {}}

        snap = self._get_snapshot(source_id, target)
        if snap is None:
            raise ValueError(f"snapshot version {target} not found")

        manifest = snap.get("manifest") or {}
        if isinstance(manifest, str):
            manifest = json.loads(manifest)

        store = self._store()
        blob_contents: Dict[str, bytes] = {}
        for h in set(manifest.values()):
            data = store.get(h)
            if data is not None:
                blob_contents[h] = data

        return {"version": target, "manifest": manifest, "blobs": blob_contents}

    def get_manifest(self, source_id: str, version: Optional[int] = None) -> dict:
        """Return just the manifest (no blob contents) — 供客户端做 diff 判断。"""
        source = self._get_source(source_id)
        if source is None:
            raise ValueError(f"source {source_id} not found")
        target = version if version is not None else int(source.get("latest_version") or 0)
        if target <= 0:
            return {"version": 0, "manifest": {}}
        snap = self._get_snapshot(source_id, target)
        if snap is None:
            raise ValueError(f"snapshot version {target} not found")
        manifest = snap.get("manifest") or {}
        if isinstance(manifest, str):
            manifest = json.loads(manifest)
        return {"version": target, "manifest": manifest}

    # ── 版本历史 + 删除（个人中心 agent 管理）────────────────

    def list_snapshots(self, source_id: str) -> list:
        """返回备份源的版本历史（新→旧），供 dashboard 展示。"""
        source = self._get_source(source_id)
        if source is None:
            raise ValueError(f"source {source_id} not found or not owned by user")
        try:
            rows = (
                self.db.table(TABLE_SNAPSHOTS)
                .select("*")
                .eq("source_id", source_id)
                .order("version")
                .execute()
                .data
            )
        except Exception:
            rows = []
        result = []
        for r in rows or []:
            manifest = r.get("manifest") or {}
            if isinstance(manifest, str):
                try:
                    manifest = json.loads(manifest)
                except (json.JSONDecodeError, TypeError):
                    manifest = {}
            result.append({
                "version": r.get("version"),
                "file_count": len(manifest) if isinstance(manifest, dict) else 0,
                "created_at": r.get("created_at"),
            })
        # 新→旧
        result.reverse()
        return result

    def delete_source(self, source_id: str) -> None:
        """删除备份源及其所有快照。blob 内容寻址存储暂不物理清理（可能被其他源复用）。"""
        source = self._get_source(source_id)
        if source is None:
            raise ValueError(f"source {source_id} not found or not owned by user")
        # 删除快照
        try:
            self.db.table(TABLE_SNAPSHOTS).delete().eq("source_id", source_id).execute()
        except Exception:
            pass
        # 删除备份源
        self.db.table(TABLE_SOURCES).delete().eq("id", source_id).eq("user_id", self.user_id).execute()

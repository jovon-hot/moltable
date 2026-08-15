"""Git-style bidirectional sync — v2 声明式 item-type 注册表.

同步协议 v2：每类数据用 ItemType 声明表名、字段映射、冲突策略、
主键列、user 作用域。同步引擎按策略分派，支持：
  - three_way      文本/字段三向 diff（memory/persona/project/decision）
  - lww            last-write-wins + 状态机（did，active→revoked 单向）
  - replace_atomic 原子替换禁 merge（credential，JWT 防篡改）
  - append_only    追加无冲突（persona_versions）

每行携带：version / base_content / updated_at（three_way 类型），
lww / replace_atomic 类型只需 updated_at（比较新旧），
append_only 类型无需协议列（总是插入新行）。

Push 协议：
  client 发送 {id, content, base_version, updated_at}
  - three_way: base_version == server version -> accept；否则 conflict
  - lww / replace_atomic: updated_at 新者覆盖旧者，旧者跳过
  - append_only: 已存在则跳过，否则插入
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ItemType:
    """声明式 item-type 注册表条目。"""

    table: str
    conflict_strategy: str = "three_way"  # three_way | lww | replace_atomic | append_only
    key_col: str = "id"                   # 主键列（did_registry 用 did）
    user_scoped: bool = True              # 是否直接带 user_id 列
    user_via_field: str | None = None     # 间接 user 关联列（credential.subject_did）
    content_field: str | None = None      # 直接存文本的列（memory.content）
    fields: tuple = ()                    # 需映射的普通列
    json_fields: tuple = ()               # 需 JSON 序列化的列（jsonb）
    list_fields: tuple = ()               # list 列（text[]，直接传 list，读时兼容 JSON 字符串）


ITEM_REGISTRY: Dict[str, ItemType] = {
    "memory": ItemType(
        table="memories",
        fields=("content", "category", "tags", "source", "confidence", "persona_id"),
        list_fields=("tags",),
    ),
    "persona": ItemType(
        table="personas",
        fields=("name", "description", "type", "system_prompt", "model_preference", "definition"),
    ),
    "project": ItemType(
        table="projects",
        fields=("name", "description", "persona_id", "knowledge_bases", "tools"),
        json_fields=("knowledge_bases", "tools"),
    ),
    "decision": ItemType(
        table="decisions",
        fields=("content", "project_id", "decided_at"),
    ),
    "did": ItemType(
        table="did_registry",
        fields=("public_key", "key_type", "platform", "agent_name", "status", "last_seen_at", "revoked_at"),
        conflict_strategy="lww",
        key_col="did",
    ),
    "credential": ItemType(
        table="credentials",
        fields=("credential_jwt", "issuer_did", "subject_did", "credential_type", "claims", "replaced_by", "expires_at", "revoked_at"),
        json_fields=("claims",),
        conflict_strategy="replace_atomic",
        user_scoped=False,
        user_via_field="subject_did",
    ),
    "persona_version": ItemType(
        table="persona_versions",
        fields=("persona_id", "version", "diff", "changelog", "snapshot"),
        json_fields=("diff", "snapshot"),
        conflict_strategy="append_only",
        user_scoped=True,  # 按 user_id 过滤,防跨用户泄露
    ),
    "profile": ItemType(
        table="profiles",
        fields=("nickname", "location", "education", "career", "values", "history"),
        json_fields=("education", "career", "values", "history"),
        conflict_strategy="lww",
        key_col="user_id",
        user_scoped=True,  # 1:1，按当前用户过滤（主键就是 user_id）
    ),
}

# 向后兼容：item_type -> table 映射
TABLE_MAP: Dict[str, str] = {k: v.table for k, v in ITEM_REGISTRY.items()}

# 服务端能力宣告：客户端可据此发现支持的 item types
CAPABILITIES = {
    "schema_version": 2,
    "item_types": {
        name: {"table": spec.table, "conflict_strategy": spec.conflict_strategy}
        for name, spec in ITEM_REGISTRY.items()
    },
}


def utcnow() -> str:
    """ISO-8601 UTC timestamp (second precision)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def parse_iso(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 string to a tz-aware datetime; None on failure."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def canonical_content(item_type: str, content: Any) -> str:
    """Normalize item content to a deterministic string for diffing/compare."""
    spec = ITEM_REGISTRY.get(item_type)
    if spec is not None and spec.content_field:
        return str(content)
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except (ValueError, TypeError):
            pass
    if isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False, sort_keys=True)
    return str(content)


def three_way_diff(ours: str, base: str, theirs: str) -> str:
    """Render a git-style conflict block: <<<ours ||| base ||| theirs>>>."""
    return f"<<< ours\n{ours}\n||| base\n{base}\n||| theirs\n{theirs}\n>>>"


class SyncService:
    """Per-user sync operations against a Supabase-compatible client."""

    def __init__(self, db, user_id: str):
        self.db = db
        self.user_id = user_id
        self._dids_cache: Optional[List[str]] = None

    # ── user 作用域 helpers ──────────────────────────────

    def _get_user_dids(self) -> List[str]:
        """Return the user's DID list (for credential.subject_did filtering)."""
        if self._dids_cache is not None:
            return self._dids_cache
        try:
            rows = (
                self.db.table("did_registry")
                .select("did")
                .eq("user_id", self.user_id)
                .execute()
                .data
            )
            self._dids_cache = [r["did"] for r in rows]
        except Exception:
            self._dids_cache = []
        return self._dids_cache

    # ── item content <-> table columns ───────────────────

    @staticmethod
    def _content_to_fields(item_type: str, content: Any, updated_at: str) -> Dict[str, Any]:
        """Map a sync item's content onto table columns (registry-driven)."""
        spec = ITEM_REGISTRY[item_type]
        fields: Dict[str, Any] = {"updated_at": updated_at}
        if spec.content_field:
            fields[spec.content_field] = content
            return fields
        # 兼容纯文本 content：类型有 content 字段但客户端传了字符串时，
        # 写到 content 列并补必填的 category（NOT NULL）
        if isinstance(content, str) and "content" in spec.fields:
            fields["content"] = content
            if "category" in spec.fields:
                fields.setdefault("category", "fact")
            return fields
        data = content
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (ValueError, TypeError):
                data = {}
        if not isinstance(data, dict):
            data = {}
        for key in spec.fields:
            if key in data and data[key] is not None:
                val = data[key]
                if key in spec.json_fields and not isinstance(val, str):
                    val = json.dumps(val, ensure_ascii=False)
                fields[key] = val
        return fields

    @staticmethod
    def _content_to_payload(item_type: str, row: dict) -> Any:
        """Reconstruct the sync item content from a DB row (registry-driven)."""
        spec = ITEM_REGISTRY[item_type]
        if spec.content_field:
            return row.get(spec.content_field, "")
        data = {}
        for key in spec.fields:
            if row.get(key) is not None:
                val = row.get(key)
                if (key in spec.json_fields or key in spec.list_fields) and isinstance(val, str):
                    try:
                        val = json.loads(val)
                    except (ValueError, TypeError):
                        pass
                data[key] = val
        return data

    # ── low-level helpers ─────────────────────────────────

    def _get_row(self, spec: ItemType, item_id: str) -> Optional[dict]:
        query = self.db.table(spec.table).select("*").eq(spec.key_col, item_id)
        if spec.user_scoped:
            query = query.eq("user_id", self.user_id)
        elif spec.user_via_field:
            dids = self._get_user_dids()
            if not dids:
                return None
            query = query.in_(spec.user_via_field, dids)
        rows = query.limit(1).execute().data
        return rows[0] if rows else None

    def _insert(self, table: str, fields: dict) -> None:
        self.db.table(table).insert(fields).execute()

    def _update(self, spec: ItemType, item_id: str, fields: dict) -> None:
        query = self.db.table(spec.table).update(fields).eq(spec.key_col, item_id)
        if spec.user_scoped:
            query = query.eq("user_id", self.user_id)
        elif spec.user_via_field:
            dids = self._get_user_dids()
            if not dids:
                return
            query = query.in_(spec.user_via_field, dids)
        query.execute()

    def _base_fields(self, spec: ItemType, item_id: str) -> Dict[str, Any]:
        """Insert-time identity fields (id / user_id / created_at; version 由调用方按策略设置)."""
        fields: Dict[str, Any] = {spec.key_col: item_id, "created_at": utcnow()}
        if spec.user_scoped:
            fields["user_id"] = self.user_id
        return fields

    # ── public operations ─────────────────────────────────

    def push(self, items: List[dict], item_type: str) -> dict:
        """Push local changes. Never silently overwrites a divergent row."""
        spec = ITEM_REGISTRY[item_type]
        if spec.conflict_strategy == "append_only":
            return self._push_append_only(items, item_type, spec)
        if spec.conflict_strategy in ("lww", "replace_atomic"):
            return self._push_lww(items, item_type, spec)
        return self._push_three_way(items, item_type, spec)

    def _push_three_way(self, items: List[dict], item_type: str, spec: ItemType) -> dict:
        accepted: List[dict] = []
        conflicts: List[dict] = []
        now = utcnow()
        for item in items:
            item_id = item.get("id")
            if not item_id:
                continue
            updated_at = item.get("updated_at") or now
            row = self._get_row(spec, item_id)
            if row is None:
                fields = self._content_to_fields(item_type, item.get("content"), updated_at)
                fields.update(self._base_fields(spec, item_id))
                fields.update({"version": 1, "base_content": ""})
                self._insert(spec.table, fields)
                accepted.append({"id": item_id, "type": item_type, "version": 1, "updated_at": updated_at})
                continue
            server_version = int(row.get("version") or 1)
            client_base = int(item.get("base_version") or 0)
            if client_base == server_version:
                new_version = server_version + 1
                prev_payload = canonical_content(item_type, self._content_to_payload(item_type, row))
                fields = self._content_to_fields(item_type, item.get("content"), updated_at)
                fields.update({"version": new_version, "base_content": prev_payload})
                self._update(spec, item_id, fields)
                accepted.append({"id": item_id, "type": item_type, "version": new_version, "updated_at": updated_at})
            else:
                ours = canonical_content(item_type, self._content_to_payload(item_type, row))
                theirs = canonical_content(item_type, item.get("content"))
                base = row.get("base_content") or ""
                conflicts.append({
                    "id": item_id, "type": item_type,
                    "ours": ours, "base": base, "theirs": theirs,
                    "ours_version": server_version, "theirs_base_version": client_base,
                    "diff": three_way_diff(ours, base, theirs),
                })
        return {"accepted": accepted, "conflicts": conflicts}

    def _push_lww(self, items: List[dict], item_type: str, spec: ItemType) -> dict:
        """last-write-wins / replace-atomic：updated_at 新者覆盖旧者。

        did 额外带状态机：status=revoked 单向不可逆（不接受 active 覆盖 revoked）。
        """
        accepted: List[dict] = []
        conflicts: List[dict] = []
        now = utcnow()
        for item in items:
            item_id = item.get("id")
            if not item_id:
                continue
            updated_at = item.get("updated_at") or now
            content = item.get("content") or {}
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except (ValueError, TypeError):
                    content = {}
            row = self._get_row(spec, item_id)
            if row is None:
                fields = self._content_to_fields(item_type, content, updated_at)
                fields.update(self._base_fields(spec, item_id))
                fields.update({"version": 1, "base_content": ""})
                self._insert(spec.table, fields)
                accepted.append({"id": item_id, "type": item_type, "version": 1, "updated_at": updated_at})
                continue
            # 状态机保护（did）：revoked 不可逆
            if spec.table == "did_registry" and row.get("status") == "revoked" and content.get("status") != "revoked":
                conflicts.append({"id": item_id, "type": item_type, "reason": "revoked_immutable", "ours": row, "theirs": content})
                continue
            incoming_ts = parse_iso(updated_at)
            current_ts = parse_iso(row.get("updated_at"))
            if incoming_ts is not None and current_ts is not None and incoming_ts < current_ts:
                continue  # 旧数据，跳过
            new_version = int(row.get("version") or 1) + 1
            fields = self._content_to_fields(item_type, content, updated_at)
            fields.update({"version": new_version})
            self._update(spec, item_id, fields)
            accepted.append({"id": item_id, "type": item_type, "version": new_version, "updated_at": updated_at})
        return {"accepted": accepted, "conflicts": conflicts}

    def _push_append_only(self, items: List[dict], item_type: str, spec: ItemType) -> dict:
        """append-only：已存在则跳过，否则插入新行（无冲突）。"""
        accepted: List[dict] = []
        now = utcnow()
        for item in items:
            item_id = item.get("id")
            if not item_id:
                continue
            updated_at = item.get("updated_at") or now
            row = self._get_row(spec, item_id)
            if row is not None:
                accepted.append({"id": item_id, "type": item_type, "version": int(row.get("version") or 1), "updated_at": row.get("updated_at"), "skipped": True})
                continue
            fields = self._content_to_fields(item_type, item.get("content"), updated_at)
            fields.update(self._base_fields(spec, item_id))
            self._insert(spec.table, fields)
            accepted.append({"id": item_id, "type": item_type, "version": 1, "updated_at": updated_at})
        return {"accepted": accepted, "conflicts": []}

    def pull(self, since: Optional[str] = None) -> dict:
        """Return all user rows, optionally filtered by updated_at >= since."""
        result: Dict[str, list] = {}
        for item_type, spec in ITEM_REGISTRY.items():
            query = self.db.table(spec.table).select("*")
            if spec.user_scoped:
                query = query.eq("user_id", self.user_id)
            elif spec.user_via_field:
                dids = self._get_user_dids()
                if not dids:
                    result[spec.table] = []
                    continue
                query = query.in_(spec.user_via_field, dids)
            if since:
                if spec.conflict_strategy == "append_only":
                    query = query.gte("created_at", since)
                else:
                    query = query.gte("updated_at", since)
            try:
                rows = query.execute().data
            except Exception:
                rows = []  # 表缺失/查询失败 → 空列表，不阻断其他类型
            result[spec.table] = [
                {
                    "id": row.get(spec.key_col),
                    "content": self._content_to_payload(item_type, row),
                    "version": int(row.get("version") or 1),
                    "updated_at": row.get("updated_at") or row.get("created_at") or "",
                }
                for row in rows
            ]
        return result

    def resolve(self, item_id: str, item_type: str, resolved_content: Any, base_version: int) -> dict:
        """Accept a client-resolved conflict with a version bump (three_way only)."""
        spec = ITEM_REGISTRY[item_type]
        if spec.conflict_strategy != "three_way":
            raise ValueError(f"{item_type} uses {spec.conflict_strategy}, not three_way resolve")
        row = self._get_row(spec, item_id)
        if row is None:
            raise ValueError(f"{item_type} '{item_id}' not found")
        now = utcnow()
        server_version = int(row.get("version") or 1)
        new_version = max(server_version, int(base_version or 0)) + 1
        prev_payload = canonical_content(item_type, self._content_to_payload(item_type, row))
        fields = self._content_to_fields(item_type, resolved_content, now)
        fields.update({"version": new_version, "base_content": prev_payload})
        self._update(spec, item_id, fields)
        return {"ok": True, "new_version": new_version}

    def export_all(self) -> dict:
        """Snapshot all user data as a JSON-able dict (v2)."""
        data = self.pull()
        data["exported_at"] = utcnow()
        data["schema_version"] = 2
        data["capabilities"] = CAPABILITIES
        return data

    def import_data(self, payload: dict) -> dict:
        """Merge an export payload. Older rows are skipped, never regressed."""
        now = utcnow()
        imported = updated = skipped = 0
        for item_type, spec in ITEM_REGISTRY.items():
            for item in payload.get(spec.table) or []:
                item_id = item.get("id")
                if not item_id:
                    continue
                row = self._get_row(spec, item_id)
                if row is None:
                    fields = self._content_to_fields(item_type, item.get("content"), item.get("updated_at") or now)
                    fields.update(self._base_fields(spec, item_id))
                    fields["version"] = int(item.get("version") or 1)
                    fields["base_content"] = ""
                    self._insert(spec.table, fields)
                    imported += 1
                    continue
                incoming_ts = parse_iso(item.get("updated_at"))
                current_ts = parse_iso(row.get("updated_at"))
                if incoming_ts is not None and current_ts is not None and incoming_ts < current_ts:
                    skipped += 1
                    continue
                if spec.conflict_strategy in ("lww", "replace_atomic"):
                    new_version = int(row.get("version") or 1) + 1
                    fields = self._content_to_fields(item_type, item.get("content"), item.get("updated_at") or now)
                    fields.update({"version": new_version})
                    self._update(spec, item_id, fields)
                    updated += 1
                    continue
                server_version = int(row.get("version") or 1)
                new_version = max(server_version, int(item.get("version") or 1)) + 1
                prev_payload = canonical_content(item_type, self._content_to_payload(item_type, row))
                fields = self._content_to_fields(item_type, item.get("content"), item.get("updated_at") or now)
                fields.update({"version": new_version, "base_content": prev_payload})
                self._update(spec, item_id, fields)
                updated += 1
        return {"imported": imported, "updated": updated, "skipped": skipped}

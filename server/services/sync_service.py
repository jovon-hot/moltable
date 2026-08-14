"""Git-style bidirectional sync: conflict detection, versioning, three-way diff.

Each row in memories/personas/projects carries:
- version:      integer, bumped on every accepted write
- base_content: content of the previous version (the common ancestor used
                to build the three-way diff when a conflict is reported)
- updated_at:   UTC timestamp of the last write

Push protocol:
  client sends {id, content, base_version, updated_at}
  - base_version == server version -> accept, version + 1
  - base_version != server version -> conflict: report ours / base / theirs
Resolve protocol:
  client sends {id, type, resolved_content, base_version} -> accept with bump.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

TABLE_MAP = {
    "memory": "memories",
    "persona": "personas",
    "project": "projects",
}


def utcnow() -> str:
    """ISO-8601 UTC timestamp (second precision, e.g. 2026-08-12T09:00:00Z)."""
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
    if item_type == "memory":
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

    # ── item content <-> table columns ───────────────────

    @staticmethod
    def _content_to_fields(item_type: str, content: Any, updated_at: str) -> Dict[str, Any]:
        """Map a sync item's content onto table columns for insert/update."""
        fields: Dict[str, Any] = {"updated_at": updated_at}
        if item_type == "memory":
            fields["content"] = content
            return fields
        data = content
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (ValueError, TypeError):
                data = {}
        if not isinstance(data, dict):
            data = {}
        if item_type == "persona":
            for key in (
                "name",
                "description",
                "type",
                "system_prompt",
                "model_preference",
                "definition",
            ):
                if key in data and data[key] is not None:
                    fields[key] = data[key]
        elif item_type == "project":
            for key in ("name", "description", "persona_id"):
                if key in data and data[key] is not None:
                    fields[key] = data[key]
            for key in ("knowledge_bases", "tools"):
                if key in data and data[key] is not None:
                    fields[key] = data[key]
        return fields

    @staticmethod
    def _content_to_payload(item_type: str, row: dict) -> Any:
        """Reconstruct the sync item content from a DB row."""
        if item_type == "memory":
            return row.get("content", "")
        if item_type == "persona":
            return {
                key: row[key]
                for key in (
                    "name",
                    "description",
                    "type",
                    "system_prompt",
                    "model_preference",
                    "definition",
                )
                if row.get(key) is not None
            }
        data = {
            key: row[key]
            for key in ("name", "description", "persona_id")
            if row.get(key) is not None
        }
        for key in ("knowledge_bases", "tools"):
            value = row.get(key)
            if value:
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except (ValueError, TypeError):
                        pass
                data[key] = value
        return data

    # ── low-level helpers ─────────────────────────────────

    def _get_row(self, table: str, item_id: str) -> Optional[dict]:
        rows = (
            self.db.table(table)
            .select("*")
            .eq("id", item_id)
            .eq("user_id", self.user_id)
            .limit(1)
            .execute()
            .data
        )
        return rows[0] if rows else None

    def _insert(self, table: str, fields: dict) -> None:
        self.db.table(table).insert(fields).execute()

    def _update(self, table: str, item_id: str, fields: dict) -> None:
        (
            self.db.table(table)
            .update(fields)
            .eq("id", item_id)
            .eq("user_id", self.user_id)
            .execute()
        )

    # ── public operations ─────────────────────────────────

    def push(self, items: List[dict], item_type: str) -> dict:
        """Push local changes. Never silently overwrites a divergent row."""
        accepted: List[dict] = []
        conflicts: List[dict] = []
        table = TABLE_MAP[item_type]
        now = utcnow()
        for item in items:
            item_id = item.get("id")
            if not item_id:
                continue
            updated_at = item.get("updated_at") or now
            row = self._get_row(table, item_id)
            if row is None:
                fields = self._content_to_fields(item_type, item.get("content"), updated_at)
                fields.update(
                    {
                        "id": item_id,
                        "user_id": self.user_id,
                        "version": 1,
                        "base_content": "",
                        "created_at": now,
                    }
                )
                self._insert(table, fields)
                accepted.append(
                    {"id": item_id, "type": item_type, "version": 1, "updated_at": updated_at}
                )
                continue

            server_version = int(row.get("version") or 1)
            client_base = int(item.get("base_version") or 0)
            if client_base == server_version:
                new_version = server_version + 1
                prev_payload = canonical_content(
                    item_type, self._content_to_payload(item_type, row)
                )
                fields = self._content_to_fields(item_type, item.get("content"), updated_at)
                fields.update({"version": new_version, "base_content": prev_payload})
                self._update(table, item_id, fields)
                accepted.append(
                    {
                        "id": item_id,
                        "type": item_type,
                        "version": new_version,
                        "updated_at": updated_at,
                    }
                )
            else:
                ours = canonical_content(item_type, self._content_to_payload(item_type, row))
                theirs = canonical_content(item_type, item.get("content"))
                base = row.get("base_content") or ""
                conflicts.append(
                    {
                        "id": item_id,
                        "type": item_type,
                        "ours": ours,
                        "base": base,
                        "theirs": theirs,
                        "ours_version": server_version,
                        "theirs_base_version": client_base,
                        "diff": three_way_diff(ours, base, theirs),
                    }
                )
        return {"accepted": accepted, "conflicts": conflicts}

    def pull(self, since: Optional[str] = None) -> dict:
        """Return all user rows, optionally filtered by updated_at >= since."""
        result: Dict[str, list] = {}
        for item_type, table in TABLE_MAP.items():
            query = self.db.table(table).select("*").eq("user_id", self.user_id)
            if since:
                query = query.gte("updated_at", since)
            rows = query.execute().data
            result[table] = [
                {
                    "id": row.get("id"),
                    "content": self._content_to_payload(item_type, row),
                    "version": int(row.get("version") or 1),
                    "updated_at": row.get("updated_at") or "",
                }
                for row in rows
            ]
        return result

    def resolve(
        self, item_id: str, item_type: str, resolved_content: Any, base_version: int
    ) -> dict:
        """Accept a client-resolved conflict with a version bump."""
        table = TABLE_MAP[item_type]
        row = self._get_row(table, item_id)
        if row is None:
            raise ValueError(f"{item_type} '{item_id}' not found")
        now = utcnow()
        server_version = int(row.get("version") or 1)
        new_version = max(server_version, int(base_version or 0)) + 1
        prev_payload = canonical_content(item_type, self._content_to_payload(item_type, row))
        fields = self._content_to_fields(item_type, resolved_content, now)
        fields.update({"version": new_version, "base_content": prev_payload})
        self._update(table, item_id, fields)
        return {"ok": True, "new_version": new_version}

    def export_all(self) -> dict:
        """Snapshot all user data as a JSON-able dict."""
        data = self.pull()
        data["exported_at"] = utcnow()
        data["schema_version"] = 1
        return data

    def import_data(self, payload: dict) -> dict:
        """Merge an export payload. Older rows are skipped, never regressed."""
        now = utcnow()
        imported = updated = skipped = 0
        for item_type, table in TABLE_MAP.items():
            for item in payload.get(table) or []:
                item_id = item.get("id")
                if not item_id:
                    continue
                row = self._get_row(table, item_id)
                if row is None:
                    fields = self._content_to_fields(
                        item_type, item.get("content"), item.get("updated_at") or now
                    )
                    fields.update(
                        {
                            "id": item_id,
                            "user_id": self.user_id,
                            "version": int(item.get("version") or 1),
                            "base_content": "",
                            "created_at": now,
                        }
                    )
                    self._insert(table, fields)
                    imported += 1
                    continue
                incoming_ts = parse_iso(item.get("updated_at"))
                current_ts = parse_iso(row.get("updated_at"))
                if incoming_ts is not None and current_ts is not None and incoming_ts < current_ts:
                    skipped += 1
                    continue
                server_version = int(row.get("version") or 1)
                new_version = max(server_version, int(item.get("version") or 1)) + 1
                prev_payload = canonical_content(
                    item_type, self._content_to_payload(item_type, row)
                )
                fields = self._content_to_fields(
                    item_type, item.get("content"), item.get("updated_at") or now
                )
                fields.update({"version": new_version, "base_content": prev_payload})
                self._update(table, item_id, fields)
                updated += 1
        return {"imported": imported, "updated": updated, "skipped": skipped}

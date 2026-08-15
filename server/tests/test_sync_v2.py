"""Tests: sync v2 声明式注册表 — 新类型冲突策略（did/credential/persona_version/decision）。"""

from services.sync_service import SyncService, ITEM_REGISTRY


class FakeResp:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, db, name):
        self.db = db
        self.name = name
        self._mode = None
        self._eqs = []
        self._ins = None
        self._insert_payload = None
        self._update_payload = None

    def select(self, *cols):
        self._mode = "select"
        return self

    def eq(self, col, val):
        self._eqs.append((col, val))
        return self

    def in_(self, col, vals):
        self._ins = (col, vals)
        return self

    def limit(self, n):
        return self

    def gte(self, col, val):
        return self

    def insert(self, payload):
        self._mode = "insert"
        self._insert_payload = payload
        return self

    def update(self, payload):
        self._mode = "update"
        self._update_payload = payload
        return self

    def execute(self):
        if self._mode == "insert":
            row = dict(self._insert_payload)
            key = row.get("id") or row.get("did") or row.get("user_id")
            self.db._ensure(self.name)[key] = row
            return FakeResp([row])
        if self._mode == "update":
            for col, val in self._eqs:
                for r in list(self.db._ensure(self.name).values()):
                    if r.get(col) == val:
                        r.update(dict(self._update_payload))
            return FakeResp([])
        if self._mode == "select":
            rows = list(self.db._ensure(self.name).values())
            for col, val in self._eqs:
                rows = [r for r in rows if r.get(col) == val]
            if self._ins:
                col, vals = self._ins
                rows = [r for r in rows if r.get(col) in vals]
            return FakeResp(rows)
        return FakeResp([])


class FakeDB:
    def __init__(self, tables=None):
        self.tables = tables or {}

    def _ensure(self, name):
        if name not in self.tables:
            self.tables[name] = {}
        return self.tables[name]

    def table(self, name):
        return FakeTable(self, name)


def test_registry_has_new_types():
    assert set(ITEM_REGISTRY) >= {"memory", "persona", "project", "decision", "did", "credential", "persona_version"}


def test_did_lww_new_insert():
    """新 DID：插入。"""
    db = FakeDB()
    svc = SyncService(db, "user-1")
    r = svc.push([{"id": "did:web:test", "content": {"public_key": "pk", "status": "active"}, "updated_at": "2026-01-01T00:00:00Z"}], "did")
    assert len(r["accepted"]) == 1 and not r["conflicts"]
    assert db.tables["did_registry"]["did:web:test"]["status"] == "active"


def test_did_revoked_immutable():
    """DID 状态机：revoked 不可逆，active 覆盖 revoked → conflict。"""
    db = FakeDB({"did_registry": {"did:web:test": {"did": "did:web:test", "status": "revoked", "version": 3, "updated_at": "2026-01-02T00:00:00Z", "user_id": "user-1"}}})
    svc = SyncService(db, "user-1")
    r = svc.push([{"id": "did:web:test", "content": {"public_key": "pk", "status": "active"}, "updated_at": "2026-01-03T00:00:00Z"}], "did")
    assert not r["accepted"]
    assert any(c.get("reason") == "revoked_immutable" for c in r["conflicts"])


def test_did_lww_older_skipped():
    """LWW：旧 updated_at → 跳过。"""
    db = FakeDB({"did_registry": {"did:web:test": {"did": "did:web:test", "status": "active", "version": 5, "updated_at": "2026-01-05T00:00:00Z", "user_id": "user-1"}}})
    svc = SyncService(db, "user-1")
    r = svc.push([{"id": "did:web:test", "content": {"public_key": "pk", "status": "active"}, "updated_at": "2026-01-01T00:00:00Z"}], "did")
    assert not r["accepted"] and not r["conflicts"]


def test_credential_replace_atomic():
    """Credential：JWT 原子替换，无 conflict。"""
    db = FakeDB({"credentials": {"cred-1": {"id": "cred-1", "version": 2, "updated_at": "2026-01-01T00:00:00Z", "subject_did": "did:sub"}},
                 "did_registry": {"did:sub": {"did": "did:sub", "user_id": "user-1"}}})
    svc = SyncService(db, "user-1")
    r = svc.push([{"id": "cred-1", "content": {"credential_jwt": "eyJ...", "issuer_did": "did:issuer", "subject_did": "did:sub", "credential_type": "MemoryHealth", "claims": {"score": 0.9}}, "updated_at": "2026-01-02T00:00:00Z"}], "credential")
    assert len(r["accepted"]) == 1 and not r["conflicts"]
    assert db.tables["credentials"]["cred-1"]["credential_jwt"] == "eyJ..."


def test_persona_version_append_only():
    """persona_version：已存在则跳过。"""
    db = FakeDB({"persona_versions": {"pv-1": {"id": "pv-1", "version": 1, "updated_at": "2026-01-01T00:00:00Z", "user_id": "user-1"}}})
    svc = SyncService(db, "user-1")
    r = svc.push([{"id": "pv-1", "content": {"persona_id": "p1", "version": 2, "snapshot": {}}, "updated_at": "2026-01-02T00:00:00Z"}], "persona_version")
    assert len(r["accepted"]) == 1 and r["accepted"][0].get("skipped") is True


def test_decision_three_way_conflict():
    """decision：three_way，base_version 不匹配 → conflict。"""
    db = FakeDB({"decisions": {"d1": {"id": "d1", "version": 3, "base_content": "old", "updated_at": "2026-01-01T00:00:00Z", "user_id": "user-1"}}})
    svc = SyncService(db, "user-1")
    r = svc.push([{"id": "d1", "content": {"content": "新决策"}, "base_version": 1, "updated_at": "2026-01-02T00:00:00Z"}], "decision")
    assert not r["accepted"] and r["conflicts"]


def test_credential_user_via_subject_did_no_user_id():
    """credential 无 user_id 列：insert 不带 user_id。"""
    db = FakeDB({"did_registry": {"did:web:my-agent": {"did": "did:web:my-agent", "user_id": "user-1"}}})
    svc = SyncService(db, "user-1")
    svc.push([{"id": "cred-1", "content": {"credential_jwt": "eyJ...", "subject_did": "did:web:my-agent", "credential_type": "X", "issuer_did": "i", "claims": {}}, "updated_at": "2026-01-01T00:00:00Z"}], "credential")
    assert "user_id" not in db.tables["credentials"]["cred-1"]

def test_profile_lww_new_insert():
    """profile：1:1，主键 user_id，lww 同步。"""
    db = FakeDB()
    svc = SyncService(db, "user-1")
    r = svc.push([{"id": "user-1", "content": {"nickname": "阿福", "location": "北京", "values": ["忍耐", "不将就"]}, "updated_at": "2026-01-01T00:00:00Z"}], "profile")
    assert len(r["accepted"]) == 1 and not r["conflicts"]
    assert db.tables["profiles"]["user-1"]["nickname"] == "阿福"


def test_profile_phone_not_in_sync_content():
    """phone 不进同步协议：注册表 fields 不含 phone。"""
    spec = ITEM_REGISTRY["profile"]
    assert "phone" not in spec.fields and "phone_encrypted" not in spec.fields
    assert "nickname" in spec.fields


def test_phone_encrypt_decrypt_roundtrip():
    """phone AES-256-GCM 加解密往返。"""
    import os
    import base64
    os.environ["PROFILE_PHONE_KEY"] = base64.b64encode(b"k" * 32).decode()
    import importlib
    import services.profile_crypto as pc
    importlib.reload(pc)
    ct = pc.encrypt_phone("18600042931")
    assert ct != "18600042931"  # 已加密
    assert pc.decrypt_phone(ct) == "18600042931"  # 解密还原


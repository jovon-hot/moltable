"""Tests: backup_service — 文件级快照 + CAS 内容寻址（P1）。"""

from services.backup_service import BackupService, MemoryBlobStore, sha256_bytes


class FakeResp:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, db, name):
        self.db = db
        self.name = name
        self._mode = None
        self._eqs = []
        self._insert_payload = None
        self._update_payload = None
        self._order = None
        self._limit = None

    def select(self, *cols):
        self._mode = "select"
        return self

    def eq(self, col, val):
        self._eqs.append((col, val))
        return self

    def limit(self, n):
        self._limit = n
        return self

    def order(self, col, **kw):
        self._order = col
        return self

    def insert(self, payload):
        self._mode = "insert"
        self._insert_payload = payload
        return self

    def update(self, payload):
        self._mode = "update"
        self._update_payload = payload
        return self

    def delete(self):
        self._mode = "delete"
        return self

    def execute(self):
        if self._mode == "insert":
            row = dict(self._insert_payload)
            key = row.get("id") or row.get("user_id")
            self.db._ensure(self.name)[key] = row
            return FakeResp([row])
        if self._mode == "update":
            for col, val in self._eqs:
                for r in list(self.db._ensure(self.name).values()):
                    if r.get(col) == val:
                        r.update(dict(self._update_payload))
            return FakeResp([])
        if self._mode == "delete":
            for col, val in self._eqs:
                self.db.tables[self.name] = {
                    k: v for k, v in self.db._ensure(self.name).items() if v.get(col) != val
                }
            return FakeResp([])
        if self._mode == "select":
            rows = list(self.db._ensure(self.name).values())
            for col, val in self._eqs:
                rows = [r for r in rows if r.get(col) == val]
            if self._limit is not None:
                rows = rows[: self._limit]
            return FakeResp(rows)
        return FakeResp([])


class FakeDB:
    def __init__(self):
        self.tables = {}

    def _ensure(self, name):
        if name not in self.tables:
            self.tables[name] = {}
        return self.tables[name]

    def table(self, name):
        return FakeTable(self, name)


def make_service():
    db = FakeDB()
    store = MemoryBlobStore()
    svc = BackupService(db, "user-1", blob_store=store)
    return svc, db, store


def test_create_and_list_source():
    svc, db, _ = make_service()
    src = svc.create_source("hermes", "hermes-mac-pro")
    assert src["id"]
    assert src["latest_version"] == 0

    sources = svc.list_sources()
    assert len(sources) == 1
    assert sources[0]["agent_type"] == "hermes"
    assert sources[0]["name"] == "hermes-mac-pro"


def test_push_first_snapshot_and_pull():
    svc, db, store = make_service()
    src = svc.create_source("hermes", "hermes-mac-pro")

    content_sool = b"# SOUL.md\nI am A Fu\n"
    content_agents = b"# AGENTS.md\nrules\n"
    manifest = {
        "self/SOUL.md": sha256_bytes(content_sool),
        "self/AGENTS.md": sha256_bytes(content_agents),
    }
    blobs = {
        manifest["self/SOUL.md"]: content_sool,
        manifest["self/AGENTS.md"]: content_agents,
    }

    result = svc.push(src["id"], manifest, blobs)
    assert result.version == 1
    assert result.stored_blobs == 2
    assert result.skipped_blobs == 0

    # 确认 blob 已入库
    assert store.exists(manifest["self/SOUL.md"])
    assert store.exists(manifest["self/AGENTS.md"])

    # pull 还原
    pulled = svc.pull(src["id"])
    assert pulled["version"] == 1
    assert pulled["manifest"] == manifest
    assert pulled["blobs"][manifest["self/SOUL.md"]] == content_sool
    assert pulled["blobs"][manifest["self/AGENTS.md"]] == content_agents


def test_push_incremental_cas_dedup():
    """第二次 push：只有变化文件重传，未变文件 hash 复用（CAS 去重）。"""
    svc, db, store = make_service()
    src = svc.create_source("hermes", "hermes-mac-pro")

    c1 = b"v1 soul"
    c2 = b"v1 skills"
    m1 = {"self/SOUL.md": sha256_bytes(c1), "self/skills/SKILL.md": sha256_bytes(c2)}
    svc.push(src["id"], m1, {m1[k]: v for k, v in [("self/SOUL.md", c1), ("self/skills/SKILL.md", c2)]})

    # 只改 SOUL.md
    c1_new = b"v2 soul updated"
    c2_same = c2
    m2 = {"self/SOUL.md": sha256_bytes(c1_new), "self/skills/SKILL.md": sha256_bytes(c2_same)}
    result = svc.push(src["id"], m2, {m2["self/SOUL.md"]: c1_new})

    assert result.version == 2
    assert result.stored_blobs == 1  # 只有 SOUL.md 重传
    assert result.skipped_blobs == 0

    # 版本链正确
    pulled_latest = svc.pull(src["id"])
    assert pulled_latest["version"] == 2
    assert pulled_latest["manifest"]["self/SOUL.md"] == sha256_bytes(c1_new)

    # 能拉取历史版本 v1
    pulled_v1 = svc.pull(src["id"], version=1)
    assert pulled_v1["manifest"]["self/SOUL.md"] == sha256_bytes(c1)


def test_push_skip_existing_blob_on_server():
    """客户端重复上传同一 hash（如换终端已存在），服务端跳过。"""
    svc, db, store = make_service()
    src = svc.create_source("hermes", "hermes-mac-pro")

    c = b"same content"
    h = sha256_bytes(c)
    # 第一次 push
    svc.push(src["id"], {"self/SOUL.md": h}, {h: c})
    # 第二次 push 同样内容（模拟另一终端），应 skipped
    result = svc.push(src["id"], {"self/SOUL.md": h}, {h: c})
    assert result.stored_blobs == 0
    assert result.skipped_blobs == 1
    assert result.version == 2


def test_pull_empty_source():
    svc, db, _ = make_service()
    src = svc.create_source("hermes", "hermes-mac-pro")
    pulled = svc.pull(src["id"])
    assert pulled["version"] == 0
    assert pulled["manifest"] == {}


def test_push_source_not_owned():
    svc, db, _ = make_service()
    # 另一个用户创建 source
    other_svc = BackupService(db, "user-2", blob_store=MemoryBlobStore())
    src = other_svc.create_source("hermes", "other-user-source")
    try:
        svc.push(src["id"], {"self/x": "sha256:abc"}, {})
        assert False, "should raise"
    except ValueError:
        pass


def test_manifest_only_endpoint():
    svc, db, _ = make_service()
    src = svc.create_source("hermes", "hermes-mac-pro")
    c = b"hello"
    m = {"self/SOUL.md": sha256_bytes(c)}
    svc.push(src["id"], m, {m["self/SOUL.md"]: c})

    got = svc.get_manifest(src["id"])
    assert got["version"] == 1
    assert got["manifest"] == m


def test_list_snapshots_returns_newest_first():
    """版本历史：新→旧，含 file_count。"""
    svc, db, _ = make_service()
    src = svc.create_source("hermes", "hermes-mac-pro")
    c1 = b"v1"
    m1 = {"self/SOUL.md": sha256_bytes(c1)}
    svc.push(src["id"], m1, {m1["self/SOUL.md"]: c1})
    c2 = b"v2 soul"
    m2 = {"self/SOUL.md": sha256_bytes(c2), "self/AGENTS.md": sha256_bytes(b"agents")}
    svc.push(src["id"], m2, {m2["self/SOUL.md"]: c2, m2["self/AGENTS.md"]: b"agents"})

    snaps = svc.list_snapshots(src["id"])
    assert len(snaps) == 2
    assert snaps[0]["version"] == 2  # 新→旧
    assert snaps[0]["file_count"] == 2
    assert snaps[1]["version"] == 1
    assert snaps[1]["file_count"] == 1


def test_list_snapshots_unauthorized():
    svc, db, _ = make_service()
    other_svc = BackupService(db, "user-2", blob_store=MemoryBlobStore())
    src = other_svc.create_source("hermes", "other-source")
    try:
        svc.list_snapshots(src["id"])
        assert False, "should raise"
    except ValueError:
        pass


def test_delete_source_removes_source_and_snapshots():
    svc, db, _ = make_service()
    src = svc.create_source("hermes", "hermes-mac-pro")
    c = b"v1"
    m = {"self/SOUL.md": sha256_bytes(c)}
    svc.push(src["id"], m, {m["self/SOUL.md"]: c})

    svc.delete_source(src["id"])
    assert svc.list_sources() == []
    # 快照也应被删
    assert db.tables.get("snapshots", {}) == {}


def test_delete_source_unauthorized():
    svc, db, _ = make_service()
    other_svc = BackupService(db, "user-2", blob_store=MemoryBlobStore())
    src = other_svc.create_source("hermes", "other-source")
    try:
        svc.delete_source(src["id"])
        assert False, "should raise"
    except ValueError:
        pass

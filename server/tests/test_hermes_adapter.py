"""Tests: hermes_adapter — 灵魂资产扫描 + 排除规则 + 引用。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "client"))

from hermes_adapter import (
    build_manifest,
    collect_files,
    scan_directory,
    scan_references,
    scan_soul_assets,
    sha256_bytes,
)


def _write(tmp_path, rel, content: bytes):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)
    return p


def test_scan_soul_assets_基本文件(tmp_path):
    _write(tmp_path, "SOUL.md", b"# soul\nI am A Fu")
    _write(tmp_path, "AGENTS.md", b"# agents")
    _write(tmp_path, "memories/MEMORY.md", b"# memory")
    _write(tmp_path, "skills/moltable/SKILL.md", b"# skill")

    files = scan_soul_assets(str(tmp_path))
    assert "self/SOUL.md" in files
    assert "self/AGENTS.md" in files
    assert "self/memories/MEMORY.md" in files
    assert "self/skills/moltable/SKILL.md" in files
    assert files["self/SOUL.md"] == b"# soul\nI am A Fu"


def test_scan_excludes_db_and_secrets(tmp_path):
    """流水账 db 和敏感文件必须被排除。"""
    _write(tmp_path, "SOUL.md", b"# soul")
    _write(tmp_path, "state.db", b"BIG BINARY DATA")
    _write(tmp_path, "state.db-wal", b"wal")
    _write(tmp_path, "state.db-shm", b"shm")
    _write(tmp_path, ".env", b"API_KEY=secret")
    _write(tmp_path, "memories/secret.key", b"private")
    _write(tmp_path, "memories/real.md", b"real memory")

    files = scan_soul_assets(str(tmp_path))
    keys = set(files.keys())
    assert "self/SOUL.md" in keys
    assert "self/memories/real.md" in keys
    assert "self/state.db" not in keys
    assert "self/state.db-wal" not in keys
    assert "self/.env" not in keys
    assert "self/memories/secret.key" not in keys


def test_scan_excludes_nested_db_and_git(tmp_path):
    _write(tmp_path, "skills/x/y.db", b"db")
    _write(tmp_path, "skills/a/SKILL.md", b"skill")
    _write(tmp_path, "memories/.git/config", b"git")
    _write(tmp_path, "node_modules/pkg/index.js", b"js")

    files = scan_soul_assets(str(tmp_path))
    keys = set(files.keys())
    assert "self/skills/a/SKILL.md" in keys
    assert "self/skills/x/y.db" not in keys
    assert "self/memories/.git/config" not in keys
    assert "self/node_modules/pkg/index.js" not in keys


def test_scan_references_logical_name(tmp_path):
    kb = tmp_path / "ailib"
    _write(kb, "00-raw/note.md", b"raw note")
    _write(kb, "x-core/_GATE.md", b"gate")

    files = scan_references([{"logical_name": "ailib", "path": str(kb)}])
    assert "refs/ailib/00-raw/note.md" in files
    assert "refs/ailib/x-core/_GATE.md" in files


def test_build_manifest_deterministic(tmp_path):
    files = {"self/a.md": b"aaa", "self/b.md": b"bbb"}
    m = build_manifest(files)
    assert m["self/a.md"] == sha256_bytes(b"aaa")
    assert m["self/b.md"] == sha256_bytes(b"bbb")


def test_collect_files_merges_self_and_refs(tmp_path):
    ws = tmp_path / "hermes"
    kb = tmp_path / "kb"
    _write(ws, "SOUL.md", b"soul")
    _write(kb, "doc.md", b"doc")

    config = {
        "workspace": str(ws),
        "references": [{"logical_name": "kb", "path": str(kb)}],
        "exclude": [],
    }
    files = collect_files(config)
    assert "self/SOUL.md" in files
    assert "refs/kb/doc.md" in files

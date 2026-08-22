"""Hermes adapter — 扫描灵魂资产文件（P1 客户端核心）。

职责：定位 Hermes 的「灵魂资产」文件（SOUL.md / AGENTS.md / memories/ / skills/），
排除「流水账」（state.db / *.db-wal / FTS 索引）和敏感文件（.env / *.key）。

设计要点（见设计文档 v0.3）：
- 只备份「记忆/灵魂资产」，不备份「流水账」
- 引用（references）：用户显式声明的外部知识库，逻辑名映射路径
- 排除规则：默认排除 db / 密钥 / 依赖目录
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
from typing import Dict, List, Optional, Tuple

DEFAULT_EXCLUDE = [
    ".env", ".env.*", "*.key", "*.pem", "*.p12",
    "*.db", "*.db-wal", "*.db-shm", "*.sqlite", "*.sqlite-wal", "*.sqlite-shm",
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".DS_Store", "*.pyc",
]

# Hermes 的灵魂资产清单（相对 ~/.hermes/）
HERMES_SOUL_PATHS = [
    "SOUL.md",
    "AGENTS.md",
    "USER.md",
    "memories",
    "skills",
]


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _matches_exclude(rel_path: str, exclude: List[str]) -> bool:
    """判断相对路径是否命中排除规则（支持 glob，如 *.db 匹配任意目录下的 .db）。"""
    parts = rel_path.split("/")
    for pattern in exclude:
        # 匹配完整相对路径
        if fnmatch.fnmatch(rel_path, pattern):
            return True
        # 匹配任意一层（如 "*.db" 应命中 "memories/x.db"）
        for part in parts:
            if fnmatch.fnmatch(part, pattern):
                return True
        # 目录匹配（如 "node_modules" 命中 "x/node_modules/y.js"）
        if "/" not in pattern and pattern in parts:
            return True
    return False


def scan_directory(root: str, exclude: List[str]) -> Dict[str, bytes]:
    """递归扫描目录，返回 {相对路径: 文件字节}，应用排除规则。"""
    result: Dict[str, bytes] = {}
    root = os.path.abspath(os.path.expanduser(root))
    if not os.path.isdir(root):
        return result
    for dirpath, dirnames, filenames in os.walk(root):
        # 提前剪枝排除目录
        dirnames[:] = [d for d in dirnames if not _matches_exclude(d + "/", exclude)]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            if _matches_exclude(rel, exclude):
                continue
            try:
                with open(full, "rb") as f:
                    result[rel] = f.read()
            except (OSError, PermissionError):
                continue
    return result


def scan_soul_assets(workspace: str, exclude: Optional[List[str]] = None) -> Dict[str, bytes]:
    """扫描 Hermes 灵魂资产，返回 {self/相对路径: 文件字节}。

    workspace = ~/.hermes/，只扫 HERMES_SOUL_PATHS 里列的文件和目录。
    """
    exclude = exclude or DEFAULT_EXCLUDE
    workspace = os.path.abspath(os.path.expanduser(workspace))
    result: Dict[str, bytes] = {}

    for rel in HERMES_SOUL_PATHS:
        full = os.path.join(workspace, rel)
        if os.path.isfile(full):
            if not _matches_exclude(rel, exclude):
                try:
                    with open(full, "rb") as f:
                        result[f"self/{rel}"] = f.read()
                except (OSError, PermissionError):
                    continue
        elif os.path.isdir(full):
            scanned = scan_directory(full, exclude)
            for sub_rel, data in scanned.items():
                result[f"self/{rel}/{sub_rel}"] = data
    return result


def scan_references(references: List[dict], exclude: Optional[List[str]] = None) -> Dict[str, bytes]:
    """扫描用户声明的外部引用，返回 {refs/逻辑名/相对路径: 文件字节}。"""
    exclude = exclude or DEFAULT_EXCLUDE
    result: Dict[str, bytes] = {}
    for ref in references or []:
        logical = ref.get("logical_name", "").strip()
        path = ref.get("path", "").strip()
        if not logical or not path:
            continue
        scanned = scan_directory(path, exclude)
        for rel, data in scanned.items():
            result[f"refs/{logical}/{rel}"] = data
    return result


def build_manifest(files: Dict[str, bytes]) -> Dict[str, str]:
    """由文件字节生成 manifest（path → hash）。"""
    return {path: sha256_bytes(data) for path, data in files.items()}


def load_config(path: Optional[str] = None) -> dict:
    """加载备份配置 ~/.moltable/backup.json（不存在则用默认）。"""
    path = path or os.path.expanduser("~/.moltable/backup.json")
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def default_config() -> dict:
    return {
        "agent_type": "hermes",
        "workspace": "~/.hermes",
        "references": [],
        "exclude": list(DEFAULT_EXCLUDE),
    }


def collect_files(config: dict) -> Dict[str, bytes]:
    """按配置收集全部待备份文件（self/ + refs/）。"""
    workspace = config.get("workspace") or "~/.hermes"
    exclude = config.get("exclude") or DEFAULT_EXCLUDE
    references = config.get("references") or []

    files = scan_soul_assets(workspace, exclude)
    files.update(scan_references(references, exclude))
    return files

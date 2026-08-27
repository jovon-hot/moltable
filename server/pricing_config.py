"""定价配置 — 配额与套餐文案集中管理，支持环境变量覆盖（后台可配置）。

价格本身由 Stripe Dashboard 配置（见 routes/billing.py get_pricing()）。
本文件管理「非价格」维度：同步配额展示（Agent/Persona/记忆）+ 备份配额（备份源/存储）。

套餐 features = 前端定价页展示（同步指标为主，备份存储为次）。
套餐 limits = 后端备份配额强制执行（backup_sources / storage_gb），
同步配额（identities/personas/memories/agents）由 services/quota.py 强制执行。

所有字段都可用环境变量覆盖，改 Railway 环境变量即可生效，无需改代码：
  MOLTABLE_FREE_SOURCES      Free 备份源数量（默认 3）
  MOLTABLE_FREE_STORAGE_GB   Free 存储空间 GB（默认 0.1 = 100MB）
  MOLTABLE_PRO_SOURCES       Pro 备份源数量（默认 10）
  MOLTABLE_PRO_STORAGE_GB    Pro 存储空间 GB（默认 1）
  MOLTABLE_ULTRA_SOURCES     Ultra 备份源数量（默认 100）
  MOLTABLE_ULTRA_STORAGE_GB  Ultra 存储空间 GB（默认 10）
"""

import os


def _num(name: str, default: float) -> float:
    """解析数值环境变量（支持小数，如 0.1GB = 100MB）。"""
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


# ── 配额（后台可配置）──────────────────────────────
FREE_SOURCES = _int("MOLTABLE_FREE_SOURCES", 3)
FREE_STORAGE_GB = _num("MOLTABLE_FREE_STORAGE_GB", 0.1)     # 100MB
PRO_SOURCES = _int("MOLTABLE_PRO_SOURCES", 10)
PRO_STORAGE_GB = _num("MOLTABLE_PRO_STORAGE_GB", 1.0)       # 1GB
ULTRA_SOURCES = _int("MOLTABLE_ULTRA_SOURCES", 100)
ULTRA_STORAGE_GB = _num("MOLTABLE_ULTRA_STORAGE_GB", 10.0)  # 10GB


def _fmt_storage(gb: float) -> str:
    if gb < 0:
        return "无限备份存储"
    if gb < 1:
        return f"{int(round(gb * 1024))}MB 备份存储"
    return f"{int(gb)}GB 备份存储"


def build_plan(plan: str) -> dict:
    """构建套餐的 limits + features（对齐「Agent 在线同步」定位）。"""
    if plan == "free":
        sources, storage = FREE_SOURCES, FREE_STORAGE_GB
        features = [
            "1 个 Agent",
            "2 个 Persona",
            "100 条记忆",
            "基础 MCP 工具",
            "版本管理",
        ]
        limits = {"backup_sources": sources, "storage_gb": storage}
    elif plan == "ultra":
        sources, storage = ULTRA_SOURCES, ULTRA_STORAGE_GB
        features = [
            "无限 Agent",
            "无限 Persona",
            "5 万条记忆",
            _fmt_storage(storage),
            "优先支持",
        ]
        limits = {"backup_sources": sources, "storage_gb": storage}
    else:  # pro
        sources, storage = PRO_SOURCES, PRO_STORAGE_GB
        features = [
            "5 个 Agent",
            "10 个 Persona",
            "1 万条记忆",
            _fmt_storage(storage),
            "跨框架迁移（即将推出）",
        ]
        limits = {"backup_sources": sources, "storage_gb": storage}

    return {"features": features, "limits": limits}

"""
Quota 检查 — 按 plan 限制资源使用量

PLAN LIMITS (默认值，可用环境变量覆盖):
  free:  1 identity, 2 personas, 100 memories, 1 agent, 50 api/day
  pro:   3 identities, 10 personas, 10000 memories, 5 agents, 500 api/day
  team:  10 identities, 999999 personas, 50000 memories, 999999 agents, 2000 api/day

环境变量命名: MOLTABLE_QUOTA_{PLAN}_{RESOURCE}（PLAN ∈ FREE/PRO/TEAM，
RESOURCE ∈ IDENTITIES/PERSONAS/MEMORIES/AGENTS/API_CALLS_PER_DAY）。
未设置或非法值时回退到上述默认值。例如:
  MOLTABLE_QUOTA_FREE_PERSONAS=2
  MOLTABLE_QUOTA_PRO_MEMORIES=10000
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException

logger = logging.getLogger(__name__)

_DEFAULT_PLAN_LIMITS = {
    "free": {
        "identities": 1,
        "personas": 2,
        "memories": 100,
        "agents": 1,
        "api_calls_per_day": 50,
    },
    "pro": {
        "identities": 3,
        "personas": 10,
        "memories": 10_000,
        "agents": 5,
        "api_calls_per_day": 500,
    },
    "team": {
        "identities": 10,
        "personas": 999_999,
        "memories": 50_000,
        "agents": 999_999,
        "api_calls_per_day": 2_000,
    },
}


def _load_plan_limits() -> dict:
    """构建 PLAN_LIMITS：优先读取环境变量，未配置或非法值回退到默认值。"""
    limits = {}
    for plan, resources in _DEFAULT_PLAN_LIMITS.items():
        limits[plan] = {}
        for resource, default in resources.items():
            env_key = f"MOLTABLE_QUOTA_{plan.upper()}_{resource.upper()}"
            raw = os.getenv(env_key)
            if raw is not None and raw.strip():
                try:
                    limits[plan][resource] = int(raw.strip())
                    continue
                except ValueError:
                    pass
            limits[plan][resource] = default
    return limits


PLAN_LIMITS = _load_plan_limits()

PLAN_NAMES = {
    "free": "免费版",
    "pro": "Pro",
    "team": "Team",
}

PLAN_FEATURES = {
    "free": [
        "1 个 AI 身份",
        "2 个 Persona",
        "100 条记忆",
        "1 个 Agent",
        "基础 MCP 工具",
    ],
    "pro": [
        "3 个 AI 身份",
        "10 个 Persona",
        "10,000 条记忆",
        "5 个 Agent",
        "浏览器插件",
        "优先支持",
    ],
    "team": [
        "10 个 AI 身份",
        "无限 Persona",
        "50,000 条记忆",
        "团队记忆库",
        "共享 Persona",
        "管理面板",
        "优先支持",
    ],
}


def get_plan_limit(user_id: str, resource: str) -> int:
    """获取某用户某资源的限额。返回上限值。"""
    plan = _get_user_plan(user_id)
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"]).get(resource, 0)


def check_trial_expiry(user_id: str) -> Optional[str]:
    """
    检查试用是否过期；过期且未订阅则自动降级为 free。

    规则：
    - 已订阅（stripe_subscription_id 存在）→ 保持付费 plan，不受试用期影响
    - 未订阅（仅试用）→ expires_at 过期则降级 free
    返回降级后（或未降级）的生效 plan。
    """
    from app_state import supabase

    if supabase is None:
        return "free"

    try:
        result = (
            supabase.table("users")
            .select("plan", "expires_at", "stripe_subscription_id")
            .eq("id", user_id)
            .execute()
        )
        row = result.data[0] if result.data else {}
    except Exception as e:
        logger.error("check_trial_expiry 查询失败 user=%s: %s", user_id, e)
        return None

    plan = row.get("plan", "free")
    if plan not in ("pro", "team"):
        return plan

    # 已付费订阅：不受试用期限制，直接返回当前 plan
    if row.get("stripe_subscription_id"):
        return plan

    expires_at = row.get("expires_at")
    if not expires_at:
        return plan

    if isinstance(expires_at, str):
        try:
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        except ValueError:
            return plan

    if expires_at < datetime.now(timezone.utc):
        # 试用过期且未订阅 → 自动降级 free
        # 加 stripe_subscription_id IS NULL 条件，避免竞态覆盖 webhook 刚写入的订阅
        try:
            supabase.table("users").update({"plan": "free"}).eq("id", user_id).is_("stripe_subscription_id", "null").execute()
        except Exception as e:
            logger.error("check_trial_expiry 降级写库失败 user=%s: %s", user_id, e)
        return "free"

    return plan


def check_quota(user_id: str, resource: str, current_count: int, operation: str = "create"):
    """
    检查是否超出配额。超出则抛 402 Payment Required。

    Args:
        user_id: 用户 ID
        resource: 资源类型 (memories/personas/agents/identities)
        current_count: 当前已有数量
        operation: 操作描述（用于错误消息）
    """
    limit = get_plan_limit(user_id, resource)
    if current_count >= limit:
        plan = _get_user_plan(user_id)
        raise HTTPException(
            status_code=402,
            detail={
                "error": "quota_exceeded",
                "resource": resource,
                "limit": limit,
                "current": current_count,
                "plan": plan,
                "plan_name": PLAN_NAMES.get(plan, plan),
                "upgrade_url": "/dashboard/settings?upgrade=pro",
                "message": f"{PLAN_NAMES.get(plan, plan)} {resource} 限额 {limit} 已达。升级 Pro 解锁更多。",
            },
        )
    return limit - current_count  # 返回剩余配额


def get_usage(user_id: str) -> dict:
    """获取用户当前用量统计。"""
    from app_state import supabase

    if supabase is None:
        return _empty_usage()

    try:
        memories = _count(supabase, "memories", user_id)
        # Persona count: use InMemoryPersonaStore in SQLite mode
        try:
            from app_state import _is_sqlite

            if _is_sqlite:
                from services.persona_store import get_persona_store

                all_p = get_persona_store().list(user_id)
                personas = sum(1 for p in all_p if p.get("user_id") == user_id)
            else:
                personas = _count(supabase, "personas", user_id)
        except Exception:
            personas = _count(supabase, "personas", user_id)
        agents = _count(supabase, "did_registry", user_id)
        api_keys = _count(supabase, "api_keys", user_id, "is_active", True)
        plan = _get_user_plan(user_id)
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])

        return {
            "plan": plan,
            "plan_name": PLAN_NAMES.get(plan, plan),
            "usage": {
                "memories": {"used": memories, "limit": limits["memories"]},
                "personas": {"used": personas, "limit": limits["personas"]},
                "agents": {"used": agents, "limit": limits["agents"]},
                "identities": {"used": 1, "limit": limits["identities"]},
                "api_keys": {"used": api_keys, "limit": 10},
            },
        }
    except Exception:
        return _empty_usage()


def _count(supabase, table: str, user_id: str, extra_field: str = None, extra_value=None) -> int:
    """计数某表某用户的记录数。"""
    try:
        q = supabase.table(table).select("id", count="exact").eq("user_id", user_id)
        if extra_field:
            q = q.eq(extra_field, extra_value)
        result = q.execute()
        return getattr(result, "count", len(result.data)) if result else 0
    except Exception:
        return 0


def _get_user_plan(user_id: str) -> str:
    plan = check_trial_expiry(user_id)
    # 查询失败（None）时 fail-open 返回 pro，避免瞬时故障把付费用户锁成 free 配额
    return plan if plan is not None else "pro"


def _empty_usage() -> dict:
    free_limits = PLAN_LIMITS["free"]
    return {
        "plan": "free",
        "plan_name": "免费版",
        "usage": {
            "memories": {"used": 0, "limit": free_limits["memories"]},
            "personas": {"used": 0, "limit": free_limits["personas"]},
            "agents": {"used": 0, "limit": free_limits["agents"]},
            "identities": {"used": 1, "limit": free_limits["identities"]},
            "api_keys": {"used": 0, "limit": 10},
        },
    }

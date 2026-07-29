"""
Quota 检查 — 按 plan 限制资源使用量

PLAN LIMITS:
  free:  1 identity, 1 persona, 100 memories, 1 agent, 50 api/day
  pro:   3 identities, 10 personas, 10000 memories, 5 agents, 500 api/day
  team:  10 identities, 无限 personas, 50000 memories, 无限制 agents, 2000 api/day
"""

from fastapi import HTTPException

PLAN_LIMITS = {
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

PLAN_NAMES = {
    "free": "免费版",
    "pro": "Pro",
    "team": "Team",
}

PLAN_PRICES = {
    "free": {"monthly": 0, "yearly": 0},
    "pro": {"monthly": 19, "yearly": 149},
    "team": {"monthly": 39, "yearly": 399},
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
    # 默认 free plan
    from app_state import supabase
    if supabase is None:
        return PLAN_LIMITS["free"].get(resource, 0)

    try:
        result = supabase.table("users").select("plan").eq("id", user_id).execute()
        plan = (result.data[0].get("plan", "free") if result.data else "free")
    except Exception:
        plan = "free"

    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"]).get(resource, 0)


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
    from app_state import supabase
    if supabase is None:
        return "free"
    try:
        result = supabase.table("users").select("plan").eq("id", user_id).execute()
        return (result.data[0].get("plan", "free") if result.data else "free")
    except Exception:
        return "free"


def _empty_usage() -> dict:
    return {
        "plan": "free",
        "plan_name": "免费版",
        "usage": {
            "memories": {"used": 0, "limit": 100},
            "personas": {"used": 0, "limit": 2},
            "agents": {"used": 0, "limit": 1},
            "identities": {"used": 1, "limit": 1},
            "api_keys": {"used": 0, "limit": 10},
        },
    }

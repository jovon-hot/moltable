"""Billing routes — free trial activation (Stripe deferred).

激活即获得 90 天 Pro 体验，无需支付信息。
后续收费功能待 Stripe 账户开通后再接入。
"""
import os
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from app_state import limiter, supabase, _is_sqlite
from routes.auth import get_user

logger = logging.getLogger("moltable.billing")

router = APIRouter(prefix="/api/billing", tags=["billing"])

# ── 免费试用配置 ───────────────────────────────
TRIAL_DAYS = int(os.getenv("MOLTABLE_TRIAL_DAYS", "90"))
TRIAL_ACTIVE = os.getenv("MOLTABLE_TRIAL_ACTIVE", "true").lower() in ("1", "true", "yes")

# ── 用户计划元数据 ───────────────────────────────
TRIAL_PLANS = {
    "pro": {
        "plan": "pro", "plan_name": "Pro (限时体验)",
        "limits": {"identities": 3, "personas": 10, "memories": 10000, "agents": 5, "api_calls_per_day": 500},
    },
    "team": {
        "plan": "team", "plan_name": "Team (限时体验)",
        "limits": {"identities": 10, "personas": -1, "memories": 50000, "agents": -1, "api_calls_per_day": 2000},
    },
}


class ActivateRequest(BaseModel):
    plan: str = Field(default="pro", pattern=r"^(pro|team)$")
    accept_terms: bool = Field(default=True)


# ═══════════════════════════════════════════════════
#  激活免费试用
# ═══════════════════════════════════════════════════

@router.post("/activate")
@limiter.limit("10/minute")
async def activate_trial(request: Request, body: ActivateRequest,
                         user_id: str = Depends(get_user)):
    """激活 90 天 Pro/Team 免费试用。一次调用，即时生效。"""
    if not TRIAL_ACTIVE:
        raise HTTPException(503, "Trial activation is currently disabled")

    plan_info = TRIAL_PLANS.get(body.plan, TRIAL_PLANS["pro"])
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=TRIAL_DAYS)

    if supabase is not None and not _is_sqlite:
        try:
            # 更新 users.plan（最简单可靠的方案）
            supabase.table("users").update({
                "plan": plan_info["plan"],
            }).eq("id", user_id).execute()
            logger.info("Trial activated: user=%s plan=%s", user_id, body.plan)
        except Exception as e:
            logger.warning("Trial activation DB update failed (non-fatal): %s", e)

    return {
        "activated": True,
        "plan": plan_info["plan"],
        "plan_name": plan_info["plan_name"],
        "trial_days": TRIAL_DAYS,
        "expires_at": expires_at.isoformat(),
        "limits": plan_info["limits"],
        "message": f"Pro 体验已激活，{TRIAL_DAYS} 天有效。尽情使用！",
    }


# ═══════════════════════════════════════════════════
#  订阅状态查询
# ═══════════════════════════════════════════════════

@router.get("/subscription")
@limiter.limit("60/minute")
async def get_subscription(request: Request, user_id: str = Depends(get_user)):
    """返回当前用户的订阅状态（含试用过期时间）"""
    if supabase is None or _is_sqlite:
        return {"plan": "free", "status": "active"}

    try:
        resp = supabase.table("users").select("plan").eq("id", user_id).single().execute()
        if resp.data:
            plan = resp.data.get("plan", "free")
            return {
                "plan": plan,
                "plan_name": "Pro 体验中" if plan == "pro" else "Free",
                "status": "trialing" if plan == "pro" else "active",
            }
    except Exception:
        pass
    return {"plan": "free", "status": "active"}


# ═══════════════════════════════════════════════════
#  计划列表（公开）
# ═══════════════════════════════════════════════════

@router.get("/plans")
@limiter.limit("120/minute")
def get_plans(request: Request):
    """返回当前可用计划。Stripe 暂未接入，全部限时免费。"""
    return {
        "mode": "free_trial",
        "trial_days": TRIAL_DAYS,
        "message": "Stripe 收款账户暂未开通。当前所有 Pro 功能限时免费体验。",
        "free": {
            "name": "Free",
            "price_monthly": 0,
            "price_yearly": 0,
            "features": [
                "1 个 AI Agent 身份",
                "2 个 Persona",
                "100 条记忆",
                "项目环境地图",
                "MCP 工具 (8 个)",
                "基础 API 访问 (50/天)",
            ],
            "limits": {"identities": 1, "personas": 2, "memories": 100, "agents": 1, "api_calls_per_day": 50},
        },
        "pro": {
            "name": "Pro · 限时体验",
            "price_monthly": 0,
            "price_yearly": 0,
            "badge": f"🔥 {TRIAL_DAYS}天免费",
            "features": [
                "3 个 AI Agent 身份",
                "10 个 Persona",
                "10,000 条记忆",
                "Agent 自动发现",
                "Skills 内容同步",
                "MCP 密钥加密存储",
                "记忆离线缓存",
                "完整 API 访问 (500/天)",
            ],
            "limits": {"identities": 3, "personas": 10, "memories": 10000, "agents": 5, "api_calls_per_day": 500},
            "trial_days": TRIAL_DAYS,
            "note": "Stripe 接入后恢复 ¥19/月。早鸟用户有专属优惠。",
        },
        "team": {
            "name": "Team · 限时体验",
            "price_monthly": 0,
            "price_yearly": 0,
            "features": [
                "10 个 AI Agent 身份",
                "无限 Persona",
                "50,000 条记忆",
                "团队共享记忆库",
                "优先支持",
                "完整 API 访问 (2000/天)",
            ],
            "limits": {"identities": 10, "personas": -1, "memories": 50000, "agents": -1, "api_calls_per_day": 2000},
            "trial_days": TRIAL_DAYS,
            "note": "联系 hi@moltable.ai 开通团队试用",
        },
    }

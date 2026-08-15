"""Billing routes — free trial activation (Stripe deferred).

激活即获得 90 天 Pro 体验，无需支付信息。
后续收费功能待 Stripe 账户开通后再接入。
"""

import logging
import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app_state import _is_sqlite, limiter, supabase
from routes.auth import get_user
from services.stripe_service import get_stripe, stripe_available

logger = logging.getLogger("moltable.billing")

router = APIRouter(prefix="/api/billing", tags=["billing"])

# ── 免费试用配置 ───────────────────────────────
TRIAL_DAYS = int(os.getenv("MOLTABLE_TRIAL_DAYS", "30"))
TRIAL_ACTIVE = os.getenv("MOLTABLE_TRIAL_ACTIVE", "true").lower() in ("1", "true", "yes")

# ── 用户计划元数据 ───────────────────────────────
TRIAL_PLANS = {
    "pro": {
        "plan": "pro",
        "plan_name": "Pro (限时体验)",
        "limits": {
            "identities": 3,
            "personas": 10,
            "memories": 10000,
            "agents": 5,
            "api_calls_per_day": 500,
        },
    },
    "team": {
        "plan": "team",
        "plan_name": "Team (限时体验)",
        "limits": {
            "identities": 10,
            "personas": -1,
            "memories": 50000,
            "agents": -1,
            "api_calls_per_day": 2000,
        },
    },
}

# ── Stripe Price ID 映射（可用环境变量覆盖）────────────────────
PRICE_IDS = {
    ("pro", "monthly"): os.getenv("STRIPE_PRICE_PRO_MONTHLY", "price_1U4YZjLkDZlUqAEdFsjo33iT"),
    ("pro", "yearly"): os.getenv("STRIPE_PRICE_PRO_YEARLY", "price_1U4YZkLkDZlUqAEdGqojLR3r"),
    ("team", "monthly"): os.getenv("STRIPE_PRICE_TEAM_MONTHLY", "price_1U4YZnLkDZlUqAEdEntKfvAC"),
    ("team", "yearly"): os.getenv("STRIPE_PRICE_TEAM_YEARLY", "price_1U4YZpLkDZlUqAEd7GvNU3kr"),
}


class ActivateRequest(BaseModel):
    plan: str = Field(default="pro", pattern=r"^(pro|team)$")
    accept_terms: bool = Field(default=True)


# ═══════════════════════════════════════════════════
#  激活免费试用
# ═══════════════════════════════════════════════════


@router.post("/activate")
@limiter.limit("10/minute")
async def activate_trial(request: Request, body: ActivateRequest, user_id: str = Depends(get_user)):
    """激活 90 天 Pro/Team 免费试用。一次调用，即时生效。"""
    if not TRIAL_ACTIVE:
        raise HTTPException(503, "Trial activation is currently disabled")

    plan_info = TRIAL_PLANS.get(body.plan, TRIAL_PLANS["pro"])
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=TRIAL_DAYS)

    if supabase is not None:
        # 拒绝重复激活：已有生效中的试用（trial_activated_at 存在且 expires_at 在未来）
        try:
            existing = (
                supabase.table("users")
                .select("trial_activated_at", "expires_at")
                .eq("id", user_id)
                .execute()
            )
            row = existing.data[0] if existing.data else {}
            if row.get("trial_activated_at") and row.get("expires_at"):
                existing_exp = row["expires_at"]
                if isinstance(existing_exp, str):
                    existing_exp = datetime.fromisoformat(existing_exp.replace("Z", "+00:00"))
                if existing_exp > now:
                    raise HTTPException(409, "Trial already active — cannot re-activate")
        except HTTPException:
            raise
        except Exception as e:
            logger.warning("Trial status check failed (non-fatal): %s", e)

        try:
            # 更新 users.plan + trial_activated_at + expires_at
            supabase.table("users").update(
                {
                    "plan": plan_info["plan"],
                    "trial_activated_at": now.isoformat(),
                    "expires_at": expires_at.isoformat(),
                }
            ).eq("id", user_id).execute()
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
            "limits": {
                "identities": 1,
                "personas": 2,
                "memories": 100,
                "agents": 1,
                "api_calls_per_day": 50,
            },
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
            "limits": {
                "identities": 3,
                "personas": 10,
                "memories": 10000,
                "agents": 5,
                "api_calls_per_day": 500,
            },
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
            "limits": {
                "identities": 10,
                "personas": -1,
                "memories": 50000,
                "agents": -1,
                "api_calls_per_day": 2000,
            },
            "trial_days": TRIAL_DAYS,
            "note": "联系 hi@moltable.ai 开通团队试用",
        },
    }


# ═══════════════════════════════════════════════════
#  Stripe Checkout（订阅）
# ═══════════════════════════════════════════════════

class CheckoutRequest(BaseModel):
    plan: str = Field(default="pro", pattern=r"^(pro|team)$")
    period: str = Field(default="monthly", pattern=r"^(monthly|yearly)$")


@router.post("/checkout")
@limiter.limit("10/minute")
async def create_checkout(request: Request, body: CheckoutRequest, user_id: str = Depends(get_user)):
    """创建 Stripe Checkout Session，返回跳转 URL。"""
    stripe = get_stripe()
    if stripe is None:
        raise HTTPException(503, "Stripe is not configured")

    price_id = PRICE_IDS.get((body.plan, body.period))
    if not price_id:
        raise HTTPException(400, "Invalid plan or period")

    base = str(request.base_url).rstrip("/")
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{base}/dashboard/settings?checkout=success",
            cancel_url=f"{base}/dashboard/settings?checkout=cancelled",
            client_reference_id=user_id,
            metadata={"user_id": user_id, "plan": body.plan, "period": body.period},
        )
        return {"url": session.url}
    except Exception as e:
        logger.error("Checkout session creation failed: %s", e)
        raise HTTPException(502, f"Stripe checkout failed: {e}")


# ═══════════════════════════════════════════════════
#  Stripe Webhook（订阅生命周期）
# ═══════════════════════════════════════════════════

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """处理 Stripe 事件：checkout 完成激活订阅，订阅删除降级 free。"""
    stripe = get_stripe()
    if stripe is None:
        raise HTTPException(503, "Stripe is not configured")

    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(400, "Webhook secret not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception:
        raise HTTPException(400, "Invalid webhook signature")

    # Stripe Event 是 StripeObject（非 dict），to_dict() 递归转成普通 dict 以支持 .get()
    event = event.to_dict() if hasattr(event, "to_dict") else event

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        plan = session.get("metadata", {}).get("plan", "pro")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        if user_id and supabase is not None:
            try:
                supabase.table("users").update({
                    "plan": plan,
                    "stripe_customer_id": customer_id,
                    "stripe_subscription_id": subscription_id,
                }).eq("id", user_id).execute()
                logger.info("Subscription activated: user=%s plan=%s", user_id, plan)
            except Exception as e:
                logger.error("Failed to update subscription: %s", e)
                raise HTTPException(500, "Failed to persist subscription activation")
    elif event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        subscription_id = sub.get("id")
        if subscription_id and supabase is not None:
            try:
                supabase.table("users").update({
                    "plan": "free",
                    "stripe_subscription_id": None,
                }).eq("stripe_subscription_id", subscription_id).execute()
                logger.info("Subscription cancelled: %s", subscription_id)
            except Exception as e:
                logger.error("Failed to downgrade subscription: %s", e)
                raise HTTPException(500, "Failed to persist subscription downgrade")

    return {"received": True}


# ═══════════════════════════════════════════════════
#  Customer Portal（自助管理订阅）
# ═══════════════════════════════════════════════════

@router.post("/portal")
@limiter.limit("10/minute")
async def create_portal(request: Request, user_id: str = Depends(get_user)):
    """创建 Customer Portal Session，让用户自助管理订阅。"""
    stripe = get_stripe()
    if stripe is None:
        raise HTTPException(503, "Stripe is not configured")

    if supabase is None or _is_sqlite:
        raise HTTPException(400, "Portal requires Supabase")

    try:
        row = supabase.table("users").select("stripe_customer_id").eq("id", user_id).single().execute()
        customer_id = row.data.get("stripe_customer_id") if row.data else None
    except Exception:
        customer_id = None

    if not customer_id:
        raise HTTPException(400, "No Stripe customer found")

    base = str(request.base_url).rstrip("/")
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{base}/dashboard/settings",
        )
        return {"url": session.url}
    except Exception as e:
        logger.error("Portal session creation failed: %s", e)
        raise HTTPException(502, f"Portal failed: {e}")

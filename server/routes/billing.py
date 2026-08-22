"""Billing routes — Stripe subscriptions (直接付费,无免费试用)."""

import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app_state import _is_sqlite, limiter, supabase
from routes.auth import get_user
from services.stripe_service import get_stripe, stripe_available
from pricing_config import (
    build_plan,
)

logger = logging.getLogger("moltable.billing")

router = APIRouter(prefix="/api/billing", tags=["billing"])

# ── Stripe Price ID 映射（可用环境变量覆盖）────────────────────
PRICE_IDS = {
    ("pro", "monthly"): os.getenv("STRIPE_PRICE_PRO_MONTHLY", "price_1U4YZjLkDZlUqAEdFsjo33iT"),
    ("pro", "yearly"): os.getenv("STRIPE_PRICE_PRO_YEARLY", "price_1U4YZkLkDZlUqAEdGqojLR3r"),
    ("team", "monthly"): os.getenv("STRIPE_PRICE_TEAM_MONTHLY", "price_1U4YZnLkDZlUqAEdEntKfvAC"),
    ("team", "yearly"): os.getenv("STRIPE_PRICE_TEAM_YEARLY", "price_1U4YZpLkDZlUqAEd7GvNU3kr"),
}


# ── 定价缓存(从 Stripe 拉取真实 USD 价格)────────────────
_pricing_cache = None
_pricing_cache_ts = 0.0
_PRICING_TTL = 300  # 秒


def get_pricing():
    """从 Stripe 拉取真实价格(USD 分)。未配置或拉取失败返回 None。

    价格源 = Stripe Price(唯一真相),通过 Stripe Dashboard 配置。
    """
    global _pricing_cache, _pricing_cache_ts
    import time
    stripe = get_stripe()
    if stripe is None:
        return None
    now = time.time()
    if _pricing_cache is not None and now - _pricing_cache_ts < _PRICING_TTL:
        return _pricing_cache
    try:
        prices = {}
        for (plan, period), pid in PRICE_IDS.items():
            p = stripe.Price.retrieve(pid)
            p = p.to_dict() if hasattr(p, "to_dict") else p
            prices[f"{plan}_{period}"] = {
                "amount": p.get("unit_amount", 0),
                "currency": p.get("currency", "usd"),
                "price_id": pid,
            }
        _pricing_cache = prices
        _pricing_cache_ts = now
        return prices
    except Exception as e:
        logger.error("Failed to fetch Stripe prices: %s", e)
        return None


# ═══════════════════════════════════════════════════
#  订阅状态查询
# ═══════════════════════════════════════════════════


@router.get("/subscription")
@limiter.limit("60/minute")
async def get_subscription(request: Request, user_id: str = Depends(get_user)):
    """返回当前用户的订阅状态"""
    if supabase is None or _is_sqlite:
        return {"plan": "free", "status": "active"}

    try:
        resp = supabase.table("users").select("plan").eq("id", user_id).single().execute()
        if resp.data:
            plan = resp.data.get("plan", "free")
            return {
                "plan": plan,
                "plan_name": "Pro" if plan == "pro" else "Free",
                "status": "active",
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
    """返回当前可用计划。Stripe 已接入则返回真实 USD 价格，否则订阅暂不可用。

    配额（备份源/存储）来自 pricing_config，后台环境变量可配置。
    """
    pricing = get_pricing()
    free_plan = build_plan("free")
    pro_plan = build_plan("pro")
    team_plan = build_plan("team")
    return {
        "mode": "paid" if pricing else "unavailable",
        "currency": "usd" if pricing else None,
        "message": None if pricing else "Stripe 收款账户暂未开通。Pro 订阅暂不可用。",
        "free": {
            "name": "Free",
            "price_monthly": 0,
            "price_yearly": 0,
            "features": free_plan["features"],
            "limits": free_plan["limits"],
        },
        "pro": {
            "name": "Pro",
            "price_monthly": pricing["pro_monthly"]["amount"] / 100 if pricing else 0,
            "price_yearly": pricing["pro_yearly"]["amount"] / 100 if pricing else 0,
            "badge": None,
            "features": pro_plan["features"],
            "limits": pro_plan["limits"],
            "note": None if pricing else "Stripe 接入后即可按 USD 订阅。",
        },
        "team": {
            "name": "Team",
            "price_monthly": pricing["team_monthly"]["amount"] / 100 if pricing else 0,
            "price_yearly": pricing["team_yearly"]["amount"] / 100 if pricing else 0,
            "features": team_plan["features"],
            "limits": team_plan["limits"],
            "note": "联系 hi@moltable.ai 开通团队订阅",
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
        # 关联已有 Stripe Customer，避免重复订阅产生多个 customer 记录
        customer_id = None
        if supabase is not None and not _is_sqlite:
            try:
                row = supabase.table("users").select("stripe_customer_id").eq("id", user_id).single().execute()
                customer_id = row.data.get("stripe_customer_id") if row.data else None
            except Exception:
                customer_id = None

        session_kwargs = {
            "mode": "subscription",
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": f"{base}/dashboard/settings?checkout=success",
            "cancel_url": f"{base}/dashboard/settings?checkout=cancelled",
            "client_reference_id": user_id,
            "metadata": {"user_id": user_id, "plan": body.plan, "period": body.period},
        }
        if customer_id:
            session_kwargs["customer"] = customer_id

        session = stripe.checkout.Session.create(**session_kwargs)
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
    event_id = event.get("id")

    # 幂等去重：Stripe 会重试失败的 webhook，已处理过的事件直接跳过，
    # 避免旧事件重放覆盖更新的订阅状态（如取消后被重新激活）。
    if event_id and supabase is not None:
        try:
            dup = supabase.table("webhook_events").select("event_id").eq("event_id", event_id).execute()
            if dup.data:
                logger.info("Duplicate webhook event ignored: %s", event_id)
                return {"received": True, "duplicate": True}
        except Exception:
            pass

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # 仅当支付成功才激活订阅，避免首期付款失败也白嫖 pro
        if session.get("payment_status") != "paid":
            logger.info("Checkout not paid, skipping activation: %s", session.get("id"))
            return {"received": True}
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

    # 处理成功后记录 event_id（用于幂等去重）
    if event_id and supabase is not None:
        try:
            supabase.table("webhook_events").insert({"event_id": event_id}).execute()
        except Exception:
            logger.warning("Failed to record webhook event: %s", event_id)

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

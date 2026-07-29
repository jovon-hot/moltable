"""Stripe checkout routes — subscription and one-time payment handling."""
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from app_state import limiter, supabase
from routes.auth import get_user

logger = logging.getLogger("moltable.stripe")

router = APIRouter(prefix="/api/billing", tags=["billing"])

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Price IDs — set in .env or Stripe Dashboard
PRICE_FREE = os.getenv("STRIPE_PRICE_FREE", "price_free_monthly")
PRICE_PRO_MONTHLY = os.getenv("STRIPE_PRICE_PRO_MONTHLY", "price_pro_monthly")
PRICE_PRO_YEARLY = os.getenv("STRIPE_PRICE_PRO_YEARLY", "price_pro_yearly")
PRICE_TEAM = os.getenv("STRIPE_PRICE_TEAM", "price_team_monthly")


def _get_stripe():
    if not STRIPE_SECRET_KEY:
        raise HTTPException(503, "Payment service not configured")
    import stripe
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe


class CheckoutRequest(BaseModel):
    plan: str = Field(..., pattern=r"^(pro|team)$")
    billing_cycle: str = Field(default="monthly", pattern=r"^(monthly|yearly)$")
    success_url: str = Field(default="http://localhost:8701/dashboard")
    cancel_url: str = Field(default="http://localhost:8701")


@router.post("/checkout")
@limiter.limit("10/minute")
async def create_checkout(request: Request, body: CheckoutRequest,
                          user_id: str = Depends(get_user)):
    """Create a Stripe Checkout Session for subscription."""
    stripe = _get_stripe()

    # 选择价格 ID：年付 vs 月付
    if body.plan == "pro":
        price_id = PRICE_PRO_YEARLY if body.billing_cycle == "yearly" else PRICE_PRO_MONTHLY
    else:
        price_id = PRICE_TEAM

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=body.success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=body.cancel_url,
            client_reference_id=user_id,
            metadata={"user_id": user_id, "plan": body.plan},
        )
        return {"url": session.url}
    except Exception as e:
        logger.error("Stripe checkout creation failed: %s", e)
        raise HTTPException(500, f"Payment service error: {str(e)}")


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events for subscription lifecycle."""
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(503, "Webhook not configured")

    stripe = _get_stripe()
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        logger.warning("Invalid Stripe webhook signature")
        raise HTTPException(400, f"Invalid signature: {str(e)}")

    # Handle subscription events
    event_type = event["type"]
    subscription = event["data"]["object"]
    user_id = subscription.get("metadata", {}).get("user_id")

    if not user_id or supabase is None:
        return {"received": True}

    try:
        if event_type == "customer.subscription.created":
            supabase.table("subscriptions").insert({
                "user_id": user_id,
                "stripe_subscription_id": subscription["id"],
                "status": subscription["status"],
                "plan": subscription["metadata"].get("plan", "pro"),
            }).execute()
            logger.info("Subscription created: user=%s", user_id)

        elif event_type == "customer.subscription.updated":
            supabase.table("subscriptions").update({
                "status": subscription["status"],
            }).eq("stripe_subscription_id", subscription["id"]).execute()

        elif event_type == "customer.subscription.deleted":
            supabase.table("subscriptions").update({
                "status": "canceled",
            }).eq("stripe_subscription_id", subscription["id"]).execute()
            logger.info("Subscription canceled: user=%s", user_id)

    except Exception as e:
        logger.error("Webhook processing error: %s", e)

    return {"received": True}


@router.get("/subscription")
@limiter.limit("60/minute")
async def get_subscription(request: Request, user_id: str = Depends(get_user)):
    """Return current subscription status for the user."""
    if supabase is None:
        return {"plan": "free", "status": "active"}

    try:
        resp = supabase.table("subscriptions") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("status", "active") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        if resp.data:
            sub = resp.data[0]
            return {
                "plan": sub.get("plan", "free"),
                "status": sub.get("status", "active"),
                "since": sub.get("created_at"),
            }
    except Exception:
        pass
    return {"plan": "free", "status": "active"}


@router.get("/plans")
@limiter.limit("120/minute")
def get_plans(request: Request):
    """Return available plans with pricing (no auth required)."""
    from services.quota import PLAN_FEATURES
    return {
        "free": {
            "name": "Free",
            "price_monthly": 0,
            "price_yearly": 0,
            "features": PLAN_FEATURES["free"],
            "limits": {"identities": 1, "personas": 2, "memories": 100, "agents": 1, "api_calls_per_day": 50},
        },
        "pro": {
            "name": "Pro",
            "price_monthly": 19,
            "price_yearly": 149,
            "yearly_savings_pct": 35,
            "features": PLAN_FEATURES["pro"],
            "limits": {"identities": 3, "personas": 10, "memories": 10000, "agents": 5, "api_calls_per_day": 500},
        },
        "team": {
            "name": "Team",
            "price_monthly": 39,
            "price_yearly": 399,
            "per_seat": True,
            "features": PLAN_FEATURES["team"],
            "limits": {"identities": 10, "personas": -1, "memories": 50000, "agents": -1, "api_calls_per_day": 2000},
        },
    }

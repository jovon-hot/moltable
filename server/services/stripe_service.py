"""Stripe service — lazy init + availability check.

优雅降级：未配置 STRIPE_SECRET_KEY 时，stripe_available() 返回 False，
所有支付端点返回 503，不影响其他功能。
"""

import logging
import os

logger = logging.getLogger("moltable.stripe")

_stripe = None
_available = None


def stripe_available() -> bool:
    """True if STRIPE_SECRET_KEY is set."""
    global _available
    if _available is None:
        _available = bool(os.getenv("STRIPE_SECRET_KEY"))
    return _available


def get_stripe():
    """Return the stripe SDK module, or None if not configured."""
    global _stripe
    if not stripe_available():
        return None
    if _stripe is None:
        import stripe

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        _stripe = stripe
        logger.info("Stripe SDK initialized")
    return _stripe

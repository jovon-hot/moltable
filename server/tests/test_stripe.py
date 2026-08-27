"""Tests: Stripe subscription integration (checkout / webhook / portal)."""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from main import app
    from routes.auth import get_user

    app.dependency_overrides[get_user] = lambda: "test-user-id"
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


class TestStripeCheckout:
    def test_checkout_not_configured(self, client):
        with patch("routes.billing.get_stripe", return_value=None):
            resp = client.post("/api/billing/checkout", json={"plan": "pro", "period": "monthly"})
        assert resp.status_code == 503

    def test_checkout_returns_url(self, client):
        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.return_value = MagicMock(url="https://checkout.stripe.com/test")
        with patch("routes.billing.get_stripe", return_value=mock_stripe):
            resp = client.post("/api/billing/checkout", json={"plan": "pro", "period": "monthly"})
        assert resp.status_code == 200
        assert resp.json()["url"] == "https://checkout.stripe.com/test"

    def test_checkout_invalid_plan(self, client):
        mock_stripe = MagicMock()
        with patch("routes.billing.get_stripe", return_value=mock_stripe):
            resp = client.post("/api/billing/checkout", json={"plan": "invalid", "period": "monthly"})
        assert resp.status_code == 422  # pydantic validation

    def test_checkout_quarterly_pro_uses_quarterly_price(self, client):
        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.return_value = MagicMock(url="https://checkout.stripe.com/quarterly")
        with patch("routes.billing.get_stripe", return_value=mock_stripe):
            resp = client.post("/api/billing/checkout", json={"plan": "pro", "period": "quarterly"})
        assert resp.status_code == 200
        assert resp.json()["url"] == "https://checkout.stripe.com/quarterly"
        # 必须把季度 price ID 传给 Stripe，而不是空串或月付价
        line_items = mock_stripe.checkout.Session.create.call_args.kwargs["line_items"]
        assert line_items[0]["price"] == "price_1U8r3iLkDZlUqAEdEzNv4fF9"

    def test_checkout_quarterly_team_uses_quarterly_price(self, client):
        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.return_value = MagicMock(url="https://checkout.stripe.com/quarterly")
        with patch("routes.billing.get_stripe", return_value=mock_stripe):
            resp = client.post("/api/billing/checkout", json={"plan": "team", "period": "quarterly"})
        assert resp.status_code == 200
        line_items = mock_stripe.checkout.Session.create.call_args.kwargs["line_items"]
        assert line_items[0]["price"] == "price_1U8r3jLkDZlUqAEdhq1b6MKh"

    def test_plans_include_quarterly_prices(self, client):
        mock_stripe = MagicMock()
        mock_stripe.Price.retrieve.side_effect = lambda pid: MagicMock(
            to_dict=lambda: {
                "id": pid,
                "unit_amount": {"price_1U4YZjLkDZlUqAEdFsjo33iT": 300, "price_1U8r3iLkDZlUqAEdEzNv4fF9": 800,
                                "price_1U4YZkLkDZlUqAEdGqojLR3r": 2000,
                                "price_1U4YZnLkDZlUqAEdEntKfvAC": 600, "price_1U8r3jLkDZlUqAEdhq1b6MKh": 1600,
                                "price_1U4YZpLkDZlUqAEd7GvNU3kr": 5500}.get(pid, 0),
                "currency": "usd",
            }
        )
        with patch("routes.billing.get_stripe", return_value=mock_stripe):
            resp = client.get("/api/billing/plans")
        assert resp.status_code == 200
        body = resp.json()
        assert body["pro"]["price_quarterly"] == 8.0
        assert body["team"]["price_quarterly"] == 16.0
        assert body["pro"]["price_monthly"] == 3.0


class TestStripeWebhook:
    def test_webhook_not_configured(self, client):
        with patch("routes.billing.get_stripe", return_value=None):
            resp = client.post("/api/billing/webhook")
        assert resp.status_code == 503

    def test_webhook_missing_secret(self, client):
        mock_stripe = MagicMock()
        with patch("routes.billing.get_stripe", return_value=mock_stripe), \
             patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("STRIPE_WEBHOOK_SECRET", None)
            resp = client.post("/api/billing/webhook")
        assert resp.status_code == 400

    def test_webhook_invalid_signature(self, client):
        mock_stripe = MagicMock()
        mock_stripe.Webhook.construct_event.side_effect = Exception("bad signature")
        with patch("routes.billing.get_stripe", return_value=mock_stripe), \
             patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            resp = client.post("/api/billing/webhook")
        assert resp.status_code == 400

    def test_webhook_checkout_completed_activates_sub(self, client):
        mock_stripe = MagicMock()
        mock_stripe.Webhook.construct_event.return_value = {
            "id": "evt_123",
            "type": "checkout.session.completed",
            "data": {"object": {
                "metadata": {"user_id": "test-user-id", "plan": "pro"},
                "customer": "cus_123",
                "subscription": "sub_123",
                "payment_status": "paid",
            }},
        }
        with patch("routes.billing.get_stripe", return_value=mock_stripe), \
             patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            resp = client.post("/api/billing/webhook")
        assert resp.status_code == 200
        assert resp.json()["received"] is True

    def test_webhook_persist_failure_returns_500(self, client):
        """Supabase 更新失败 → 返回 500，让 Stripe 重试（避免订阅数据静默丢失）。"""
        mock_stripe = MagicMock()
        mock_stripe.Webhook.construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {
                "metadata": {"user_id": "test-user-id", "plan": "pro"},
                "customer": "cus_123",
                "subscription": "sub_123",
                "payment_status": "paid",
            }},
        }
        failing_supabase = MagicMock()
        failing_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = \
            Exception("db down")

        with patch("routes.billing.get_stripe", return_value=mock_stripe), \
             patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}), \
             patch("routes.billing.supabase", failing_supabase):
            resp = client.post("/api/billing/webhook")
        assert resp.status_code == 500

    def test_webhook_subscription_deleted_downgrades(self, client):
        mock_stripe = MagicMock()
        mock_stripe.Webhook.construct_event.return_value = {
            "id": "evt_456",
            "type": "customer.subscription.deleted",
            "data": {"object": {"id": "sub_123"}},
        }
        with patch("routes.billing.get_stripe", return_value=mock_stripe), \
             patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            resp = client.post("/api/billing/webhook")
        assert resp.status_code == 200
        assert resp.json()["received"] is True

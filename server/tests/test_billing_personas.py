"""Tests: billing plans + health + well-known (no auth required)."""
from fastapi.testclient import TestClient


class TestNoAuthEndpoints:
    """Endpoints that don't require authentication."""

    def test_plans_unavailable_mode(self):
        """GET /api/billing/plans 在 Stripe 未配置时返回 unavailable 模式。"""
        from main import app
        from unittest.mock import patch
        client = TestClient(app)
        with patch("routes.billing.get_pricing", return_value=None):
            resp = client.get("/api/billing/plans")
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "unavailable"
        assert data["pro"]["price_monthly"] == 0
        assert data["free"]["price_monthly"] == 0

    def test_plans_paid_mode(self):
        """GET /api/billing/plans 在 Stripe 已配置时返回真实 USD 价格。"""
        from main import app
        from unittest.mock import patch
        client = TestClient(app)
        fake_pricing = {
            "pro_monthly": {"amount": 300, "currency": "usd", "price_id": "price_x"},
            "ultra_monthly": {"amount": 500, "currency": "usd", "price_id": "price_z"},
        }
        with patch("routes.billing.get_pricing", return_value=fake_pricing):
            resp = client.get("/api/billing/plans")
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "paid"
        assert data["currency"] == "usd"
        assert data["pro"]["price_monthly"] == 3.0
        assert data["ultra"]["price_monthly"] == 5.0

    def test_health(self):
        """GET /health returns ok."""
        from main import app
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_wellknown_mcp(self):
        """GET /.well-known/mcp returns server info."""
        from main import app
        client = TestClient(app)
        resp = client.get("/.well-known/mcp")
        assert resp.status_code == 200
        assert resp.json()["server"]["name"] == "moltable"
        assert resp.json()["capabilities"]["tools"]["total"] >= 12

    def test_plans_includes_all_tiers(self):
        """Plans endpoint returns free, pro, team tiers."""
        from main import app
        client = TestClient(app)
        resp = client.get("/api/billing/plans")
        data = resp.json()
        assert "free" in data
        assert "pro" in data
        assert "ultra" in data

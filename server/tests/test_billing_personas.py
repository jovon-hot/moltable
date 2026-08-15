"""Tests: billing plans + health + well-known (no auth required)."""
from fastapi.testclient import TestClient


class TestNoAuthEndpoints:
    """Endpoints that don't require authentication."""

    def test_plans_trial_mode(self):
        """GET /api/billing/plans returns free_trial mode with ¥0 Pro."""
        from main import app
        client = TestClient(app)
        resp = client.get("/api/billing/plans")
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "free_trial"
        assert data["pro"]["price_monthly"] == 0
        assert "限时" in data["pro"]["name"]
        assert data["free"]["price_monthly"] == 0

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
        assert "team" in data
        assert data["trial_days"] == 30

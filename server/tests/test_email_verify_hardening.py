"""Tests: 邮箱验证加固 — Altcha 人机验证 + token 30 分钟有效期 + 重复验证限制。"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from altcha import Payload, create_challenge, solve_challenge

TEST_HMAC = "moltable-local-dev-altcha-secret"


def _make_altcha_payload(hmac_secret: str = TEST_HMAC) -> str:
    """生成有效的 Altcha PoW payload。"""
    challenge = create_challenge(
        algorithm="PBKDF2/SHA-256", cost=5_000, hmac_secret=hmac_secret
    )
    solution = solve_challenge(challenge)
    assert solution is not None, "测试环境无法解算 Altcha challenge"
    return Payload(challenge, solution).to_base64()


class TestEmailVerifyHardening:
    def _make_client(self, tmp_path, monkeypatch):
        import routes.auth as auth_mod
        from app_state import limiter as _limiter
        from repositories.sqlite_adapter import SQLiteClient, init_schema

        # 速率限制器是进程级单例（内存存储）— 每个测试重置，避免跨测试累积 429
        try:
            _limiter.reset()
        except Exception:
            pass

        db = SQLiteClient(str(tmp_path / "hardening_test.db"))
        init_schema(db)
        monkeypatch.setattr(auth_mod, "supabase", db)

        from main import app
        return TestClient(app), db

    def test_challenge_endpoint(self, tmp_path, monkeypatch):
        client, _ = self._make_client(tmp_path, monkeypatch)
        resp = client.get("/api/auth/challenge")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        params = body.get("parameters", {})
        assert params.get("algorithm") == "PBKDF2/SHA-256"
        assert body.get("signature"), "challenge 应带 HMAC 签名"

    def test_register_without_altcha_rejected(self, tmp_path, monkeypatch):
        client, _ = self._make_client(tmp_path, monkeypatch)
        resp = client.post("/api/auth/register", json={
            "email": "no-captcha@gmail.com",
            "password": "TestPass2026!",
            "name": "No Captcha",
        })
        assert resp.status_code == 400, resp.text
        assert "人机验证" in resp.json()["detail"]

    def test_register_with_invalid_altcha_rejected(self, tmp_path, monkeypatch):
        client, _ = self._make_client(tmp_path, monkeypatch)
        resp = client.post("/api/auth/register", json={
            "email": "bad-captcha@gmail.com",
            "password": "TestPass2026!",
            "name": "Bad Captcha",
            "altcha": "not-a-valid-payload",
        })
        assert resp.status_code == 400, resp.text

    def test_register_with_valid_altcha_sets_token_and_expiry(self, tmp_path, monkeypatch):
        client, db = self._make_client(tmp_path, monkeypatch)
        resp = client.post("/api/auth/register", json={
            "email": "valid-captcha@gmail.com",
            "password": "TestPass2026!",
            "name": "Valid",
            "altcha": _make_altcha_payload(),
        })
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["email_verified"] is False
        # token + 过期时间已落库
        rows = (
            db.table("users")
            .select("email_verify_token, email_verify_token_expires")
            .eq("email", "valid-captcha@gmail.com")
            .execute()
            .data
        )
        assert len(rows) == 1
        assert rows[0]["email_verify_token"], "应存储验证 token"
        assert rows[0]["email_verify_token_expires"], "应存储 30 分钟过期时间"

    def test_verify_email_token_expired(self, tmp_path, monkeypatch):
        """token 过期后验证链接失效。"""
        client, db = self._make_client(tmp_path, monkeypatch)
        resp = client.post("/api/auth/register", json={
            "email": "expire@gmail.com",
            "password": "TestPass2026!",
            "name": "Expire",
            "altcha": _make_altcha_payload(),
        })
        assert resp.status_code == 200, resp.text
        rows = (
            db.table("users")
            .select("email_verify_token")
            .eq("email", "expire@gmail.com")
            .execute()
            .data
        )
        token = rows[0]["email_verify_token"]
        # 手动把过期时间改成过去
        db.table("users").update(
            {"email_verify_token_expires": "2000-01-01T00:00:00+00:00"}
        ).eq("email", "expire@gmail.com").execute()
        resp = client.get(f"/api/auth/verify-email?token={token}")
        assert resp.status_code == 400
        assert "过期" in resp.text

    def test_resend_verification_rate_limited(self, tmp_path, monkeypatch):
        """注册后立即重发 → 被 5 分钟频率窗口拒绝。"""
        client, _ = self._make_client(tmp_path, monkeypatch)
        resp = client.post("/api/auth/register", json={
            "email": "resend@gmail.com",
            "password": "TestPass2026!",
            "name": "Resend",
            "altcha": _make_altcha_payload(),
        })
        assert resp.status_code == 200, resp.text
        resp = client.post("/api/auth/resend-verification", json={"email": "resend@gmail.com"})
        assert resp.status_code == 429, resp.text

    def test_resend_verification_unknown_email_obfuscated(self, tmp_path, monkeypatch):
        """未注册邮箱 → 返回模糊消息，不泄露邮箱是否存在。"""
        client, _ = self._make_client(tmp_path, monkeypatch)
        resp = client.post("/api/auth/resend-verification", json={"email": "nobody@gmail.com"})
        assert resp.status_code == 200
        assert "如果该邮箱已注册" in resp.json()["message"]

    def test_login_before_verify_rejected(self, tmp_path, monkeypatch):
        """未验证邮箱 → 登录被拦截。"""
        client, _ = self._make_client(tmp_path, monkeypatch)
        client.post("/api/auth/register", json={
            "email": "login-unverified@gmail.com",
            "password": "TestPass2026!",
            "name": "Login",
            "altcha": _make_altcha_payload(),
        })
        resp = client.post("/api/auth/login", json={
            "email": "login-unverified@gmail.com",
            "password": "TestPass2026!",
        })
        assert resp.status_code == 403
        assert "验证邮箱" in resp.json()["detail"]

    def test_login_after_verify_returns_key(self, tmp_path, monkeypatch):
        """验证邮箱后首次登录 → 生成并返回 API key；再次登录不重复返回。"""
        client, db = self._make_client(tmp_path, monkeypatch)
        client.post("/api/auth/register", json={
            "email": "login-verified@gmail.com",
            "password": "TestPass2026!",
            "name": "Login",
            "altcha": _make_altcha_payload(),
        })
        rows = db.table("users").select("email_verify_token").eq("email", "login-verified@gmail.com").execute().data
        token = rows[0]["email_verify_token"]
        verify = client.get(f"/api/auth/verify-email?token={token}")
        assert verify.status_code == 200
        # 首次登录 → 返回 key
        resp = client.post("/api/auth/login", json={
            "email": "login-verified@gmail.com",
            "password": "TestPass2026!",
        })
        assert resp.status_code == 200, resp.text
        assert resp.json()["api_key"].startswith("molt_")
        # 第二次登录 → 已有 key，不再返回
        resp2 = client.post("/api/auth/login", json={
            "email": "login-verified@gmail.com",
            "password": "TestPass2026!",
        })
        assert resp2.status_code == 200
        assert resp2.json()["api_key"] is None
        assert resp2.json()["has_api_key"] is True

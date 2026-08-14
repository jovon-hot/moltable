"""Tests: Admin API — core auth flows."""

import hashlib
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt as _jwt
import pytest
from fastapi.testclient import TestClient

import main


def _make_sb(email="admin@test.com", role="admin"):
    sb = MagicMock()
    sb.table.return_value = sb
    sb.select.return_value = sb
    sb.eq.return_value = sb
    sb.gte.return_value = sb
    sb.ilike.return_value = sb
    sb.order.return_value = sb
    sb.range.return_value = sb
    sb.insert.return_value = sb
    sb.update.return_value = sb
    sb.execute.return_value = MagicMock(
        data=[
            {
                "email": email,
                "password_hash": "mock",
                "role": role,
                "is_active": True,
            }
        ],
        count=1,
    )
    return sb


@pytest.fixture(autouse=True)
def clear_failure_store():
    import services.admin_auth as aa

    aa._failure_store.clear()


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    import app_state

    storage = app_state.limiter._limiter.storage
    for container in ("storage", "expirations", "events"):
        data = getattr(storage, container, None)
        if hasattr(data, "clear"):
            data.clear()
    yield


# ── Helpers ──


def _patch_app_state(sb=None, is_sqlite=False):
    """Returns list of started patches. Caller must stop() each."""
    import app_state
    import services.admin_auth

    patches = [
        patch.object(app_state, "supabase", sb),
        patch.object(app_state, "_is_sqlite", is_sqlite),
        patch.object(app_state, "get_error_count", return_value=0),
        patch.object(services.admin_auth, "supabase", sb),
    ]
    for p in patches:
        p.start()
    return patches


def _patch_verify(return_val=True):
    """Patch _verify_password to always return return_val."""
    import services.admin_auth

    p = patch.object(services.admin_auth, "_verify_password", return_value=return_val)
    p.start()
    return p


# ═══════════════════════════════════════════════════


class TestLogin:
    def test_success(self):
        aps = _patch_app_state(_make_sb())
        vp = _patch_verify(True)
        try:
            c = TestClient(main.app)
            r = c.post("/api/admin/login", json={"email": "admin@test.com", "password": "p" * 10})
            assert r.status_code == 200, r.text
            assert "token" in r.json()
        finally:
            for p in aps:
                p.stop()
            vp.stop()

    def test_wrong_password(self):
        aps = _patch_app_state(_make_sb())
        vp = _patch_verify(False)
        try:
            c = TestClient(main.app)
            r = c.post("/api/admin/login", json={"email": "admin@test.com", "password": "wrong"})
            assert r.status_code == 401
        finally:
            for p in aps:
                p.stop()
            vp.stop()

    def test_no_db(self):
        aps = _patch_app_state(None)
        try:
            c = TestClient(main.app)
            r = c.post("/api/admin/login", json={"email": "x@x.com", "password": "p" * 10})
            assert r.status_code == 401
        finally:
            for p in aps:
                p.stop()

    def test_bruteforce_blocks(self):
        aps = _patch_app_state(_make_sb())
        vp = _patch_verify(False)
        try:
            c = TestClient(main.app)
            for i in range(5):
                r = c.post(
                    "/api/admin/login", json={"email": "admin@test.com", "password": f"w{i}"}
                )
                assert r.status_code == 401, f"attempt {i}: {r.text}"
            r = c.post("/api/admin/login", json={"email": "admin@test.com", "password": "correct"})
            assert r.status_code == 429, r.text
        finally:
            for p in aps:
                p.stop()
            vp.stop()


class TestAuth:
    def test_no_token_rejected(self):
        aps = _patch_app_state(None)
        try:
            c = TestClient(main.app)
            assert c.get("/api/admin/stats").status_code == 401
            assert c.get("/api/admin/users").status_code == 401
            assert c.get("/api/admin/health").status_code == 401
        finally:
            for p in aps:
                p.stop()

    def test_bad_token_rejected(self):
        aps = _patch_app_state(None)
        try:
            c = TestClient(main.app)
            h = {"X-Admin-Token": "not-a-real-token"}
            assert c.get("/api/admin/stats", headers=h).status_code == 401
            assert c.get("/api/admin/health", headers=h).status_code == 401
        finally:
            for p in aps:
                p.stop()


class TestAdminSecrets:
    def test_missing_jwt_secret_raises(self):
        import services.admin_auth as aa

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError):
                aa._require_admin_secret("ADMIN_JWT_SECRET")

    def test_short_jwt_secret_raises(self):
        import services.admin_auth as aa

        with patch.dict(os.environ, {"ADMIN_JWT_SECRET": "x" * 31}, clear=True):
            with pytest.raises(RuntimeError):
                aa._require_admin_secret("ADMIN_JWT_SECRET")

    def test_missing_password_pepper_raises(self):
        import services.admin_auth as aa

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError):
                aa._require_admin_secret("ADMIN_PASSWORD_PEPPER")

    def test_valid_secret_accepted(self):
        import services.admin_auth as aa

        with patch.dict(os.environ, {"ADMIN_JWT_SECRET": "s" * 32}, clear=True):
            assert aa._require_admin_secret("ADMIN_JWT_SECRET") == "s" * 32


class TestTokenVersion:
    @staticmethod
    def _stateful_sb(**row):
        sb = MagicMock()
        state = {
            "email": "admin@test.com",
            "password_hash": "mock",
            "role": "admin",
            "is_active": True,
            "token_version": 1,
            **row,
        }
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.eq.return_value = sb
        sb.gte.return_value = sb
        sb.ilike.return_value = sb
        sb.order.return_value = sb
        sb.range.return_value = sb
        sb.insert.return_value = sb
        sb.update.return_value = sb
        sb.execute.return_value = MagicMock(data=[state], count=1)
        return sb, state

    def _login(self, c):
        r = c.post("/api/admin/login", json={"email": "admin@test.com", "password": "p" * 10})
        assert r.status_code == 200, r.text
        return r.json()["token"]

    def test_token_carries_jti_and_version(self):
        import services.admin_auth as aa

        sb, _ = self._stateful_sb()
        aps = _patch_app_state(sb)
        vp = _patch_verify(True)
        try:
            c = TestClient(main.app)
            token = self._login(c)
            claims = _jwt.decode(token, aa.ADMIN_JWT_SECRET, algorithms=["HS256"])
            assert claims["token_version"] == 1
            assert claims["jti"]
            assert claims["role"] == "admin"
        finally:
            for p in aps:
                p.stop()
            vp.stop()

    def test_disabled_account_loses_access_immediately(self):
        sb, state = self._stateful_sb()
        aps = _patch_app_state(sb)
        vp = _patch_verify(True)
        try:
            c = TestClient(main.app)
            token = self._login(c)
            h = {"X-Admin-Token": token}
            assert c.get("/api/admin/health", headers=h).status_code == 200
            state["is_active"] = False
            assert c.get("/api/admin/health", headers=h).status_code == 401
        finally:
            for p in aps:
                p.stop()
            vp.stop()

    def test_token_version_bump_invalidates_token(self):
        sb, state = self._stateful_sb()
        aps = _patch_app_state(sb)
        vp = _patch_verify(True)
        try:
            c = TestClient(main.app)
            token = self._login(c)
            h = {"X-Admin-Token": token}
            assert c.get("/api/admin/health", headers=h).status_code == 200
            state["token_version"] = 2
            assert c.get("/api/admin/health", headers=h).status_code == 401
        finally:
            for p in aps:
                p.stop()
            vp.stop()

    def test_token_without_version_rejected(self):
        import services.admin_auth as aa

        sb, _ = self._stateful_sb()
        aps = _patch_app_state(sb)
        try:
            now = datetime.now(timezone.utc)
            legacy = _jwt.encode(
                {
                    "sub": "admin@test.com",
                    "role": "admin",
                    "iat": now,
                    "exp": now + timedelta(hours=1),
                },
                aa.ADMIN_JWT_SECRET,
                algorithm="HS256",
            )
            assert aa.verify_admin_token(legacy) is None
        finally:
            for p in aps:
                p.stop()

    def test_toggle_bumps_token_version(self):
        import services.admin_auth as aa

        sb, _ = self._stateful_sb()
        aps = _patch_app_state(sb)
        try:
            aa.toggle_admin_account("admin@test.com", False)
            payload = sb.update.call_args[0][0]
            assert payload["is_active"] is False
            assert payload["token_version"] == 2
        finally:
            for p in aps:
                p.stop()


class TestLegacyPasswordMigration:
    @staticmethod
    def _legacy_hash(password: str) -> str:
        salt = os.environ["ADMIN_PASSWORD_PEPPER"][:16].encode()
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000).hex()

    def _sb_with_hash(self, stored_hash: str):
        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.eq.return_value = sb
        sb.update.return_value = sb
        sb.execute.return_value = MagicMock(
            data=[
                {
                    "email": "admin@test.com",
                    "password_hash": stored_hash,
                    "role": "admin",
                    "is_active": True,
                    "token_version": 1,
                }
            ],
            count=1,
        )
        return sb

    @staticmethod
    def _password_hash_updates(sb):
        return [
            args[0]
            for args, _ in sb.update.call_args_list
            if args and isinstance(args[0], dict) and "password_hash" in args[0]
        ]

    def test_verify_legacy_hash(self):
        import services.admin_auth as aa

        legacy = self._legacy_hash("legacy-pass-123")
        assert aa._verify_password("legacy-pass-123", legacy)
        assert not aa._verify_password("wrong-pass", legacy)

    def test_verify_new_format_still_works(self):
        import services.admin_auth as aa

        new_hash = aa._hash_password("new-pass-123")
        assert aa._verify_password("new-pass-123", new_hash)
        assert not aa._verify_password("wrong-pass", new_hash)

    def test_verify_garbage_never_passes(self):
        import services.admin_auth as aa

        for garbage in ("", "not-a-hash", "x" * 64, "0" * 63, None):
            assert not aa._verify_password("anything", garbage)

    def test_login_migrates_legacy_hash_on_success(self):
        import services.admin_auth as aa

        sb = self._sb_with_hash(self._legacy_hash("legacy-pass-123"))
        aps = _patch_app_state(sb)
        try:
            c = TestClient(main.app)
            r = c.post(
                "/api/admin/login", json={"email": "admin@test.com", "password": "legacy-pass-123"}
            )
            assert r.status_code == 200, r.text
            migrated = self._password_hash_updates(sb)
            assert migrated, "expected a password_hash migration update"
            new_hash = migrated[0]["password_hash"]
            assert not aa._is_legacy_hash(new_hash)
            assert aa._verify_password("legacy-pass-123", new_hash)
        finally:
            for p in aps:
                p.stop()

    def test_login_no_migration_on_wrong_password(self):
        import services.admin_auth as aa

        sb = self._sb_with_hash(self._legacy_hash("legacy-pass-123"))
        aps = _patch_app_state(sb)
        try:
            c = TestClient(main.app)
            r = c.post(
                "/api/admin/login", json={"email": "admin@test.com", "password": "wrong-pass"}
            )
            assert r.status_code == 401
            assert not self._password_hash_updates(sb)
        finally:
            for p in aps:
                p.stop()

    def test_login_no_migration_for_new_format(self):
        import services.admin_auth as aa

        sb = self._sb_with_hash(aa._hash_password("new-pass-123"))
        aps = _patch_app_state(sb)
        try:
            c = TestClient(main.app)
            r = c.post(
                "/api/admin/login", json={"email": "admin@test.com", "password": "new-pass-123"}
            )
            assert r.status_code == 200, r.text
            assert not self._password_hash_updates(sb)
        finally:
            for p in aps:
                p.stop()

    def test_migration_failure_does_not_block_login(self):
        import services.admin_auth as aa

        sb = self._sb_with_hash(self._legacy_hash("legacy-pass-123"))

        def flaky_update(payload):
            if "password_hash" in payload:
                raise RuntimeError("db down")
            return sb

        sb.update.side_effect = flaky_update
        aps = _patch_app_state(sb)
        try:
            c = TestClient(main.app)
            r = c.post(
                "/api/admin/login", json={"email": "admin@test.com", "password": "legacy-pass-123"}
            )
            assert r.status_code == 200, r.text
        finally:
            for p in aps:
                p.stop()

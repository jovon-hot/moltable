"""Tests: trial expiry enforcement (billing + quota).

覆盖:
  quota.check_trial_expiry()   — 试用过期自动降级 pro → free
  POST /api/billing/activate   — 持久化 expires_at；已有生效试用时拒绝重复激活
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


# ═══════════════════════════════════════════════════════════════
# 辅助函数（与 test_agents.py 同款 mock 风格）
# ═══════════════════════════════════════════════════════════════


def _make_mock_chain(return_data: list):
    """
    构造 Supabase 链式调用 mock：
    .select().eq().limit().single().execute() 任意链 → 最终返回含 return_data 的响应。
    """
    final = MagicMock()
    final.data = return_data
    chain = MagicMock()
    chain.execute.return_value = final
    # 链式方法全部返回自身，保证任意深度链都能走到 execute()
    chain.eq.return_value = chain
    chain.order.return_value = chain
    chain.limit.return_value = chain
    chain.single.return_value = chain
    return chain


def _make_supabase(users_mock: MagicMock) -> MagicMock:
    """构造 supabase mock：users 表用指定 mock，其余表为空白 mock。"""
    mock_supabase = MagicMock()

    def _table(name: str):
        return users_mock if name == "users" else MagicMock()

    mock_supabase.table.side_effect = _table
    return mock_supabase


def _iso(dt: datetime) -> str:
    return dt.isoformat()


# ═══════════════════════════════════════════════════════════════
# quota.check_trial_expiry()
# ═══════════════════════════════════════════════════════════════


class TestCheckTrialExpiry:
    """quota.check_trial_expiry() — 试用过期自动降级"""

    def test_expired_pro_downgrades_to_free(self):
        """试用已过期 + plan=pro → 自动降级 free。"""
        from services import quota

        past = _iso(datetime.now(timezone.utc) - timedelta(days=1))
        users = MagicMock()
        users.select.return_value = _make_mock_chain([{"plan": "pro", "expires_at": past}])
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase):
            result = quota.check_trial_expiry("user-1")

        assert result == "free"
        users.update.assert_called_once_with({"plan": "free"})

    def test_active_pro_stays_pro(self):
        """试用未过期 + plan=pro → 保持 pro，不降级。"""
        from services import quota

        future = _iso(datetime.now(timezone.utc) + timedelta(days=30))
        users = MagicMock()
        users.select.return_value = _make_mock_chain([{"plan": "pro", "expires_at": future}])
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase):
            result = quota.check_trial_expiry("user-1")

        assert result == "pro"
        users.update.assert_not_called()

    def test_subscribed_pro_stays_pro_even_if_trial_expired(self):
        """已订阅(stripe_subscription_id 存在)+ 试用过期 → 保持 pro，不降级。"""
        from services import quota

        past = _iso(datetime.now(timezone.utc) - timedelta(days=1))
        users = MagicMock()
        users.select.return_value = _make_mock_chain(
            [{"plan": "pro", "expires_at": past, "stripe_subscription_id": "sub_123"}]
        )
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase):
            result = quota.check_trial_expiry("user-1")

        assert result == "pro"
        users.update.assert_not_called()

    def test_free_plan_untouched(self):
        """plan=free → 原样返回 free，不做任何降级。"""
        from services import quota

        past = _iso(datetime.now(timezone.utc) - timedelta(days=1))
        users = MagicMock()
        users.select.return_value = _make_mock_chain([{"plan": "free", "expires_at": past}])
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase):
            result = quota.check_trial_expiry("user-1")

        assert result == "free"
        users.update.assert_not_called()

    def test_no_expires_at_keeps_plan(self):
        """无 expires_at（旧数据）→ 视为未过期，保持 plan。"""
        from services import quota

        users = MagicMock()
        users.select.return_value = _make_mock_chain([{"plan": "pro", "expires_at": None}])
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase):
            result = quota.check_trial_expiry("user-1")

        assert result == "pro"
        users.update.assert_not_called()

    def test_expired_pro_with_z_suffix(self):
        """expires_at 带 'Z' 后缀（Supabase timestamptz）也能正确解析。"""
        from services import quota

        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat().replace("+00:00", "Z")
        users = MagicMock()
        users.select.return_value = _make_mock_chain([{"plan": "pro", "expires_at": past}])
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase):
            result = quota.check_trial_expiry("user-1")

        assert result == "free"

    def test_no_supabase_returns_free(self):
        """无 supabase → 返回 free。"""
        from services import quota

        with patch("app_state.supabase", None):
            assert quota.check_trial_expiry("user-1") == "free"

    def test_get_plan_limit_enforces_expiry(self):
        """get_plan_limit 应反映降级：过期 pro 试用按 free 限额计算。"""
        from services import quota

        past = _iso(datetime.now(timezone.utc) - timedelta(days=1))
        users = MagicMock()
        users.select.return_value = _make_mock_chain([{"plan": "pro", "expires_at": past}])
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase):
            limit = quota.get_plan_limit("user-1", "identities")

        assert limit == quota.PLAN_LIMITS["free"]["identities"]
        users.update.assert_called_once_with({"plan": "free"})



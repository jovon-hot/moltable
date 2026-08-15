"""Tests: Stripe billing edge cases — 试用期边界 / 订阅状态链路 / webhook 异常 / checkout 边界 / 订阅保护。

补充 test_stripe.py / test_trial_expiry.py 未覆盖的场景:
  1. 试用期边界:恰好第 30 天(expires_at == now)、非法时间字符串、带时区偏移
  2. 订阅状态转换完整链路:checkout.completed → subscription.deleted → 重新订阅
  3. webhook 异常路径:重复投递、乱序投递(deleted 早于 completed)、deleted 写库失败、未知事件
  4. checkout 边界:billing_period 非法值、price 不存在、Stripe API 异常、传参断言
  5. check_trial_expiry 订阅保护边界:stripe_subscription_id 空字符串、plan=free 但 sub_id 存在
  6. portal / subscription 端点(原测试完全未覆盖)
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from main import app
    from routes.auth import get_user

    app.dependency_overrides[get_user] = lambda: "test-user-id"
    app.state.limiter.enabled = False  # 避免测试累计触发限流(10/minute)
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()
    app.state.limiter.enabled = True


# ═══════════════════════════════════════════════════════════════
# 有状态 Fake Supabase:模拟 users 行 + 记录 update 调用
# ═══════════════════════════════════════════════════════════════

class FakeSupabase:
    """有状态 fake:users 表(select/update) + webhook_events 表(select/insert 幂等去重)。"""

    def __init__(self, user_row: dict):
        self.user_row = user_row
        self.updates = []  # [(payload, eq_field, eq_value)]
        self.processed_events = set()  # 已处理的 webhook event_id

    def table(self, name):
        self._table_name = name
        return self

    def select(self, *cols):
        self._select_cols = cols
        return self

    def insert(self, payload):
        self._pending_insert = payload
        return self

    def update(self, payload):
        self._pending_payload = payload
        return self

    def eq(self, field, value):
        self._pending_eq = (field, value)
        return self

    def execute(self):
        if self._table_name == "webhook_events":
            if getattr(self, "_pending_insert", None) is not None:
                self.processed_events.add(self._pending_insert["event_id"])
                del self._pending_insert
                return MagicMock(data=[{"event_id": "recorded"}])
            eq_field, eq_value = getattr(self, "_pending_eq", (None, None))
            if eq_field == "event_id" and eq_value in self.processed_events:
                return MagicMock(data=[{"event_id": eq_value}])
            return MagicMock(data=[])
        payload = getattr(self, "_pending_payload", None)
        eq_field, eq_value = getattr(self, "_pending_eq", (None, None))
        self.updates.append((payload, eq_field, eq_value))
        if self.user_row.get(eq_field) == eq_value:
            self.user_row.update(payload)
        self._pending_payload = None
        self._pending_eq = None
        return MagicMock(data=[self.user_row])


def _make_mock_chain(return_data: list):
    final = MagicMock()
    final.data = return_data
    chain = MagicMock()
    chain.execute.return_value = final
    chain.eq.return_value = chain
    chain.order.return_value = chain
    chain.limit.return_value = chain
    chain.single.return_value = chain
    return chain


def _make_supabase(users_mock: MagicMock) -> MagicMock:
    mock_supabase = MagicMock()

    def _table(name: str):
        return users_mock if name == "users" else MagicMock()

    mock_supabase.table.side_effect = _table
    return mock_supabase


def _completed_event(user_id="test-user-id", plan="pro", sub="sub_123", cus="cus_123", event_id="evt_123", paid=True):
    return {
        "id": event_id,
        "type": "checkout.session.completed",
        "data": {"object": {
            "metadata": {"user_id": user_id, "plan": plan},
            "customer": cus,
            "subscription": sub,
            "payment_status": "paid" if paid else "unpaid",
        }},
    }


def _deleted_event(sub="sub_123", event_id="evt_456"):
    return {
        "id": event_id,
        "type": "customer.subscription.deleted",
        "data": {"object": {"id": sub}},
    }


def _webhook_post(client, event, supabase_mock, stripe_mock=None):
    """通用 webhook 请求:patch stripe + supabase + env。"""
    if stripe_mock is None:
        stripe_mock = MagicMock()
        stripe_mock.Webhook.construct_event.return_value = event
    with patch("routes.billing.get_stripe", return_value=stripe_mock), \
         patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}), \
         patch("routes.billing.supabase", supabase_mock):
        return client.post("/api/billing/webhook")


# ═══════════════════════════════════════════════════════════════
# 1. 试用期边界
# ═══════════════════════════════════════════════════════════════

class TestTrialBoundary:
    """check_trial_expiry 边界:恰好第 30 天 / 非法字符串 / 时区偏移。"""

    def test_expires_at_exactly_now_not_expired(self):
        """expires_at == now(恰好第 30 天整点)→ 不降级(代码用严格 < 判断)。"""
        from services import quota

        fixed_now = datetime(2026, 8, 15, 12, 0, 0, tzinfo=timezone.utc)
        users = MagicMock()
        users.select.return_value = _make_mock_chain(
            [{"plan": "pro", "expires_at": fixed_now.isoformat()}]
        )
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase), \
             patch("services.quota.datetime", wraps=datetime) as fake_dt:
            fake_dt.now.return_value = fixed_now
            result = quota.check_trial_expiry("user-1")

        assert result == "pro"
        users.update.assert_not_called()

    def test_expires_at_one_second_after_now_expired(self):
        """expires_at = now + 1s(第 30 天刚过)→ 降级 free。"""
        from services import quota

        fixed_now = datetime(2026, 8, 15, 12, 0, 0, tzinfo=timezone.utc)
        users = MagicMock()
        users.select.return_value = _make_mock_chain(
            [{"plan": "pro", "expires_at": (fixed_now + timedelta(seconds=1)).isoformat()}]
        )
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase), \
             patch("services.quota.datetime", wraps=datetime) as fake_dt:
            fake_dt.now.return_value = fixed_now + timedelta(seconds=2)
            result = quota.check_trial_expiry("user-1")

        assert result == "free"
        users.update.assert_called_once_with({"plan": "free"})

    def test_expires_at_invalid_string_keeps_plan(self):
        """expires_at 是非法时间字符串 → 保持 plan,不降级(容错)。"""
        from services import quota

        users = MagicMock()
        users.select.return_value = _make_mock_chain(
            [{"plan": "pro", "expires_at": "not-a-date"}]
        )
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase):
            result = quota.check_trial_expiry("user-1")

        assert result == "pro"
        users.update.assert_not_called()

    def test_expires_at_with_offset_timezone(self):
        """expires_at 带时区偏移(+08:00)且已过期 → 正确降级。"""
        from services import quota

        # 2026-08-10T12:00:00+08:00 = 2026-08-10T04:00:00Z,已过期
        users = MagicMock()
        users.select.return_value = _make_mock_chain(
            [{"plan": "pro", "expires_at": "2026-08-10T12:00:00+08:00"}]
        )
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase):
            result = quota.check_trial_expiry("user-1")

        assert result == "free"


# ═══════════════════════════════════════════════════════════════
# 2. 订阅状态转换(active → canceled → downgraded 完整链路)
# ═══════════════════════════════════════════════════════════════

class TestSubscriptionLifecycle:
    """webhook 驱动完整链路:激活 → 取消降级 → 重新订阅。"""

    def test_checkout_completed_writes_correct_fields(self, client):
        """checkout.session.completed 必须把 plan/customer/subscription 写入 users 表。"""
        fake = FakeSupabase({
            "id": "test-user-id", "plan": "free",
            "stripe_subscription_id": None, "stripe_customer_id": None,
        })
        resp = _webhook_post(client, _completed_event(), fake)
        assert resp.status_code == 200
        assert fake.updates[0][0] == {
            "plan": "pro",
            "stripe_customer_id": "cus_123",
            "stripe_subscription_id": "sub_123",
        }

    def test_checkout_completed_defaults_plan_to_pro(self, client):
        """metadata 缺 plan → 默认 pro。"""
        fake = FakeSupabase({
            "id": "test-user-id", "plan": "free",
            "stripe_subscription_id": None, "stripe_customer_id": None,
        })
        event = _completed_event()
        event["data"]["object"]["metadata"] = {"user_id": "test-user-id"}
        resp = _webhook_post(client, event, fake)
        assert resp.status_code == 200
        assert fake.updates[0][0]["plan"] == "pro"

    def test_checkout_completed_without_user_id_skips_update(self, client):
        """metadata 缺 user_id → 跳过写库,仍返回 200。"""
        mock_supabase = MagicMock()
        event = _completed_event()
        event["data"]["object"]["metadata"] = {}
        resp = _webhook_post(client, event, mock_supabase)
        assert resp.status_code == 200
        mock_supabase.table.return_value.update.assert_not_called()

    def test_deleted_writes_correct_fields_and_matches_by_sub_id(self, client):
        """subscription.deleted 必须置 plan=free + sub_id=None,并按 sub_id 匹配用户。"""
        fake = FakeSupabase({
            "id": "test-user-id", "plan": "pro",
            "stripe_subscription_id": "sub_xyz", "stripe_customer_id": "cus_123",
        })
        resp = _webhook_post(client, _deleted_event("sub_xyz"), fake)
        assert resp.status_code == 200

        # 关键:必须用 eq("stripe_subscription_id", "sub_xyz") 匹配,而不是按 user id
        payload, eq_field, eq_value = fake.updates[0]
        assert payload == {"plan": "free", "stripe_subscription_id": None}
        assert eq_field == "stripe_subscription_id"
        assert eq_value == "sub_xyz"

    def test_full_chain_activate_cancel_downgrade_resubscribe(self, client):
        """完整链路:completed(激活 pro)→ deleted(降级 free)→ completed(重新订阅 pro)。"""
        fake = FakeSupabase({
            "id": "test-user-id",
            "plan": "free",
            "stripe_subscription_id": None,
            "stripe_customer_id": None,
        })

        # ① 订阅激活
        resp = _webhook_post(client, _completed_event(sub="sub_123", cus="cus_123"), fake)
        assert resp.status_code == 200
        assert fake.user_row["plan"] == "pro"
        assert fake.user_row["stripe_subscription_id"] == "sub_123"
        assert fake.user_row["stripe_customer_id"] == "cus_123"

        # ② 取消订阅 → 降级 free
        resp = _webhook_post(client, _deleted_event("sub_123"), fake)
        assert resp.status_code == 200
        assert fake.user_row["plan"] == "free"
        assert fake.user_row["stripe_subscription_id"] is None

        # ③ 重新订阅 → 再次激活 pro
        resp = _webhook_post(client, _completed_event(sub="sub_456", cus="cus_456", event_id="evt_789"), fake)
        assert resp.status_code == 200
        assert fake.user_row["plan"] == "pro"
        assert fake.user_row["stripe_subscription_id"] == "sub_456"

        # 共 3 次写库,顺序正确(记录为 (eq_field, eq_value))
        assert [(u[1], u[2]) for u in fake.updates] == [
            ("id", "test-user-id"),
            ("stripe_subscription_id", "sub_123"),
            ("id", "test-user-id"),
        ]


# ═══════════════════════════════════════════════════════════════
# 3. webhook 异常路径
# ═══════════════════════════════════════════════════════════════

class TestWebhookAnomalies:
    """重复投递 / 乱序投递 / deleted 写库失败 / 未知事件。"""

    def test_duplicate_checkout_completed_delivery(self, client):
        """同一 checkout.completed 重复投递两次 → 第一次处理,第二次被幂等去重跳过。"""
        fake = FakeSupabase({
            "id": "test-user-id", "plan": "free",
            "stripe_subscription_id": None, "stripe_customer_id": None,
        })
        resp1 = _webhook_post(client, _completed_event(), fake)
        resp2 = _webhook_post(client, _completed_event(), fake)  # 同一 event_id
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp2.json().get("duplicate") is True
        assert len(fake.updates) == 1  # 只写库一次

    def test_duplicate_deleted_delivery(self, client):
        """同一 subscription.deleted 重复投递两次 → 均 200,第二次不误伤。"""
        fake = FakeSupabase({
            "id": "test-user-id", "plan": "pro",
            "stripe_subscription_id": "sub_123", "stripe_customer_id": "cus_123",
        })
        resp1 = _webhook_post(client, _deleted_event("sub_123"), fake)
        resp2 = _webhook_post(client, _deleted_event("sub_123"), fake)  # 同一 event_id
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp2.json().get("duplicate") is True
        assert len(fake.updates) == 1  # 只写库一次
        assert fake.user_row["plan"] == "free"

    def test_deleted_before_completed_out_of_order(self, client):
        """乱序投递:deleted 先到(此时无 sub_id 匹配)→ 200 且不误伤;completed 后到 → 正常激活。"""
        fake = FakeSupabase({
            "id": "test-user-id", "plan": "free",
            "stripe_subscription_id": None, "stripe_customer_id": None,
        })
        # deleted 先到:按 sub_id 匹配不到任何行 → 静默跳过,200
        resp1 = _webhook_post(client, _deleted_event("sub_123"), fake)
        assert resp1.status_code == 200
        assert fake.user_row["plan"] == "free"  # 未被误降级

        # completed 后到 → 正常激活
        resp2 = _webhook_post(client, _completed_event(), fake)
        assert resp2.status_code == 200
        assert fake.user_row["plan"] == "pro"

    def test_deleted_persist_failure_returns_500(self, client):
        """subscription.deleted 写库失败 → 500(与 completed 路径对称,让 Stripe 重试)。"""
        stripe_mock = MagicMock()
        stripe_mock.Webhook.construct_event.return_value = _deleted_event("sub_123")
        failing = MagicMock()
        failing.table.return_value.update.return_value.eq.return_value.execute.side_effect = \
            Exception("db down")
        # webhook_events 幂等去重 select 返回空 data(不误判重复)
        failing.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        resp = _webhook_post(client, None, failing, stripe_mock)
        assert resp.status_code == 500

    def test_unknown_event_type_returns_received(self, client):
        """未知事件类型(如 invoice.paid)→ 返回 200 received,不写库。"""
        mock_supabase = MagicMock()
        event = {"type": "invoice.paid", "data": {"object": {}}}
        resp = _webhook_post(client, event, mock_supabase)
        assert resp.status_code == 200
        assert resp.json()["received"] is True
        mock_supabase.table.return_value.update.assert_not_called()

    def test_deleted_without_subscription_id(self, client):
        """deleted 事件缺 id → 跳过写库,200。"""
        mock_supabase = MagicMock()
        event = {"type": "customer.subscription.deleted", "data": {"object": {}}}
        resp = _webhook_post(client, event, mock_supabase)
        assert resp.status_code == 200
        mock_supabase.table.return_value.update.assert_not_called()


# ═══════════════════════════════════════════════════════════════
# 4. checkout 边界
# ═══════════════════════════════════════════════════════════════

class TestCheckoutEdge:
    """checkout:billing_period 非法 / price 不存在 / Stripe API 异常 / 传参断言。"""

    def test_checkout_invalid_period_422(self, client):
        """billing_period 非法值 → 422(pydantic pattern 校验)。"""
        mock_stripe = MagicMock()
        with patch("routes.billing.get_stripe", return_value=mock_stripe):
            resp = client.post("/api/billing/checkout", json={"plan": "pro", "period": "weekly"})
        assert resp.status_code == 422

    def test_checkout_team_plan_ok(self, client):
        """team 计划也允许 checkout。"""
        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.return_value = MagicMock(url="https://checkout.stripe.com/team")
        with patch("routes.billing.get_stripe", return_value=mock_stripe):
            resp = client.post("/api/billing/checkout", json={"plan": "team", "period": "yearly"})
        assert resp.status_code == 200
        assert resp.json()["url"] == "https://checkout.stripe.com/team"

    def test_checkout_price_not_found_400(self, client):
        """PRICE_IDS 中找不到 (plan, period) 组合 → 400 Invalid plan or period。"""
        mock_stripe = MagicMock()
        with patch("routes.billing.get_stripe", return_value=mock_stripe), \
             patch("routes.billing.PRICE_IDS", {}):
            resp = client.post("/api/billing/checkout", json={"plan": "pro", "period": "monthly"})
        assert resp.status_code == 400

    def test_checkout_stripe_error_502(self, client):
        """Stripe Session.create 抛异常 → 502,不裸奔 500。"""
        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.side_effect = Exception("stripe down")
        with patch("routes.billing.get_stripe", return_value=mock_stripe):
            resp = client.post("/api/billing/checkout", json={"plan": "pro", "period": "monthly"})
        assert resp.status_code == 502

    def test_checkout_passes_correct_args_to_stripe(self, client):
        """断言传给 Stripe 的参数:mode/line_items(price id)/metadata/client_reference_id。"""
        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.return_value = MagicMock(url="https://checkout.stripe.com/test")
        with patch("routes.billing.get_stripe", return_value=mock_stripe), \
             patch("routes.billing.PRICE_IDS", {("pro", "monthly"): "price_pro_m"}), \
             patch.dict("os.environ", {}, clear=False):
            resp = client.post("/api/billing/checkout", json={"plan": "pro", "period": "monthly"})
        assert resp.status_code == 200

        kwargs = mock_stripe.checkout.Session.create.call_args.kwargs
        assert kwargs["mode"] == "subscription"
        assert kwargs["line_items"] == [{"price": "price_pro_m", "quantity": 1}]
        assert kwargs["metadata"] == {"user_id": "test-user-id", "plan": "pro", "period": "monthly"}
        assert kwargs["client_reference_id"] == "test-user-id"
        assert "checkout=success" in kwargs["success_url"]


# ═══════════════════════════════════════════════════════════════
# 5. check_trial_expiry 订阅保护边界
# ═══════════════════════════════════════════════════════════════

class TestSubscriptionGuard:
    """订阅保护边界:空字符串 sub_id / plan=free 但 sub_id 残留。"""

    def test_empty_string_subscription_id_not_protected(self):
        """stripe_subscription_id 为空字符串 '' → 视为未订阅( falsy )→ 试用过期即降级。

        风险提示:若 DB 中存了空串而非 NULL,订阅保护会失效(降级已付费用户)。
        """
        from services import quota

        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        users = MagicMock()
        users.select.return_value = _make_mock_chain(
            [{"plan": "pro", "expires_at": past, "stripe_subscription_id": ""}]
        )
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase):
            result = quota.check_trial_expiry("user-1")

        assert result == "free"
        users.update.assert_called_once_with({"plan": "free"})

    def test_free_plan_with_subscription_id_stays_free(self):
        """plan=free 但 sub_id 残留(订阅已取消、数据未清)→ 返回 free,不 update。"""
        from services import quota

        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        users = MagicMock()
        users.select.return_value = _make_mock_chain(
            [{"plan": "free", "expires_at": past, "stripe_subscription_id": "sub_old"}]
        )
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase):
            result = quota.check_trial_expiry("user-1")

        assert result == "free"
        users.update.assert_not_called()

    def test_subscription_protects_team_plan_too(self):
        """订阅保护同样适用于 team 计划。"""
        from services import quota

        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        users = MagicMock()
        users.select.return_value = _make_mock_chain(
            [{"plan": "team", "expires_at": past, "stripe_subscription_id": "sub_team"}]
        )
        mock_supabase = _make_supabase(users)

        with patch("app_state.supabase", mock_supabase):
            result = quota.check_trial_expiry("user-1")

        assert result == "team"
        users.update.assert_not_called()


# ═══════════════════════════════════════════════════════════════
# 6. portal / subscription 端点(原测试完全未覆盖)
# ═══════════════════════════════════════════════════════════════

class TestPortalEndpoint:
    """POST /api/billing/portal。"""

    def test_portal_not_configured_503(self, client):
        with patch("routes.billing.get_stripe", return_value=None):
            resp = client.post("/api/billing/portal")
        assert resp.status_code == 503

    def test_portal_sqlite_mode_400(self, client):
        """SQLite 模式(Supabase 不可用)→ 400 Portal requires Supabase。"""
        mock_stripe = MagicMock()
        with patch("routes.billing.get_stripe", return_value=mock_stripe), \
             patch("routes.billing._is_sqlite", True):
            resp = client.post("/api/billing/portal")
        assert resp.status_code == 400

    def test_portal_no_customer_400(self, client):
        """用户无 stripe_customer_id → 400 No Stripe customer found。"""
        mock_stripe = MagicMock()
        mock_supabase = MagicMock()
        row = MagicMock()
        row.data = {"stripe_customer_id": None}
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = row
        with patch("routes.billing.get_stripe", return_value=mock_stripe), \
             patch("routes.billing._is_sqlite", False), \
             patch("routes.billing.supabase", mock_supabase):
            resp = client.post("/api/billing/portal")
        assert resp.status_code == 400

    def test_portal_returns_url(self, client):
        """有 customer_id → 创建 Portal Session 并返回 url。"""
        mock_stripe = MagicMock()
        mock_stripe.billing_portal.Session.create.return_value = MagicMock(url="https://billing.stripe.com/p/session")
        mock_supabase = MagicMock()
        row = MagicMock()
        row.data = {"stripe_customer_id": "cus_123"}
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = row
        with patch("routes.billing.get_stripe", return_value=mock_stripe), \
             patch("routes.billing._is_sqlite", False), \
             patch("routes.billing.supabase", mock_supabase):
            resp = client.post("/api/billing/portal")
        assert resp.status_code == 200
        assert resp.json()["url"] == "https://billing.stripe.com/p/session"
        kwargs = mock_stripe.billing_portal.Session.create.call_args.kwargs
        assert kwargs["customer"] == "cus_123"
        assert "/dashboard/settings" in kwargs["return_url"]

    def test_portal_stripe_error_502(self, client):
        """Portal Session.create 抛异常 → 502。"""
        mock_stripe = MagicMock()
        mock_stripe.billing_portal.Session.create.side_effect = Exception("stripe down")
        mock_supabase = MagicMock()
        row = MagicMock()
        row.data = {"stripe_customer_id": "cus_123"}
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = row
        with patch("routes.billing.get_stripe", return_value=mock_stripe), \
             patch("routes.billing._is_sqlite", False), \
             patch("routes.billing.supabase", mock_supabase):
            resp = client.post("/api/billing/portal")
        assert resp.status_code == 502


class TestSubscriptionEndpoint:
    """GET /api/billing/subscription。"""

    def test_subscription_sqlite_mode_free(self, client):
        """SQLite 模式 → plan=free / status=active。"""
        with patch("routes.billing._is_sqlite", True):
            resp = client.get("/api/billing/subscription")
        assert resp.status_code == 200
        assert resp.json() == {"plan": "free", "status": "active"}

    def test_subscription_pro_trialing(self, client):
        """plan=pro → status=trialing。"""
        mock_supabase = MagicMock()
        resp_obj = MagicMock()
        resp_obj.data = {"plan": "pro"}
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = resp_obj
        with patch("routes.billing._is_sqlite", False), \
             patch("routes.billing.supabase", mock_supabase):
            resp = client.get("/api/billing/subscription")
        assert resp.status_code == 200
        assert resp.json()["plan"] == "pro"
        assert resp.json()["status"] == "trialing"

    def test_subscription_supabase_error_falls_back_free(self, client):
        """Supabase 查询异常 → 兜底 free/active,不 500。"""
        mock_supabase = MagicMock()
        mock_supabase.table.side_effect = Exception("db down")
        with patch("routes.billing._is_sqlite", False), \
             patch("routes.billing.supabase", mock_supabase):
            resp = client.get("/api/billing/subscription")
        assert resp.status_code == 200
        assert resp.json() == {"plan": "free", "status": "active"}

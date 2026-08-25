"""赠送存储额度（bonus）服务测试 — 分享/邀请 +1GB 阶梯机制。"""
import os

import pytest

os.environ.pop("SUPABASE_URL", None)
os.environ.pop("SUPABASE_SERVICE_ROLE_KEY", None)
os.environ["_HERMES_TESTING"] = "1"


@pytest.fixture
def db(tmp_path, monkeypatch):
    from repositories.sqlite_adapter import SQLiteClient, init_schema
    database = SQLiteClient(str(tmp_path / "bonus_test.db"))
    init_schema(database)
    import services.bonus_service as bs
    monkeypatch.setattr(bs, "supabase", database)
    monkeypatch.setattr(bs, "_is_sqlite", True)
    return database


def _make_user(db, uid="u1", email="a@b.com"):
    db.table("users").insert({
        "id": uid, "email": email, "password_hash": "x",
        "email_verified": 1, "bonus_storage_gb": 0,
    }).execute()


def test_grant_and_get_bonus(db):
    from services.bonus_service import grant_bonus, get_bonus_gb
    _make_user(db)
    assert get_bonus_gb("u1") == 0.0
    assert grant_bonus("u1", "share", 1.0, source="https://linkedin.com/p/1") is True
    assert get_bonus_gb("u1") == 1.0
    # 防重复：同 source 不再发
    assert grant_bonus("u1", "share", 1.0, source="https://linkedin.com/p/1") is False
    assert get_bonus_gb("u1") == 1.0
    # 不同 source 可发
    assert grant_bonus("u1", "share", 1.0, source="https://linkedin.com/p/2") is True
    assert get_bonus_gb("u1") == 2.0


def test_share_bonus_cap(db):
    from services.bonus_service import count_share_bonuses, grant_bonus, SHARE_BONUS_CAP
    _make_user(db)
    for i in range(SHARE_BONUS_CAP):
        assert grant_bonus("u1", "share", 1.0, source=f"https://linkedin.com/p/{i}") is True
    assert count_share_bonuses("u1") == SHARE_BONUS_CAP


def test_referral_bonus_on_first_backup(db):
    from services.bonus_service import get_bonus_gb, grant_referral_bonus_on_first_backup
    # 邀请人 + 被邀请人
    _make_user(db, uid="inviter", email="inviter@b.com")
    _make_user(db, uid="friend", email="friend@b.com")
    # 被邀请人通过 referral 注册
    db.table("referrals").insert({
        "id": "r1", "referrer_id": "inviter", "code": "ABC12345",
        "referred_email": "friend@b.com", "referred_user_id": "friend",
        "reward_granted": 0, "status": "claimed",
    }).execute()
    assert get_bonus_gb("inviter") == 0.0
    # 好友首次备份 → 邀请人 +1GB
    grant_referral_bonus_on_first_backup("friend")
    assert get_bonus_gb("inviter") == 1.0
    # 重复触发不重复发放
    grant_referral_bonus_on_first_backup("friend")
    assert get_bonus_gb("inviter") == 1.0

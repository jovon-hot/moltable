"""分享/邀请赠送存储额度（bonus storage）服务。

机制：
- 分享 LinkedIn 帖子 → +1GB（`share`，上限 SHARE_BONUS_CAP 次）
- 好友接受邀请并完成首次备份 → 邀请人 +1GB（`referral`，每好友一次）

额度叠加在 plan 基础存储之上（见 quota.py / backup_service.py）。
"""
import logging
import uuid
from datetime import datetime, timezone

from app_state import _is_sqlite, supabase

logger = logging.getLogger("moltable.bonus")

SHARE_BONUS_CAP = 3     # 分享送 1GB 的上限次数
SHARE_BONUS_GB = 1.0
REFERRAL_BONUS_GB = 1.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_bonus_gb(user_id: str) -> float:
    """查询用户累计赠送额度（GB）。"""
    try:
        result = supabase.table("users").select("bonus_storage_gb").eq("id", user_id).execute()
        if result.data:
            val = result.data[0].get("bonus_storage_gb") or 0
            return float(val)
    except Exception as e:
        logger.warning("bonus lookup failed for %s: %s", user_id, e)
    return 0.0


def count_share_bonuses(user_id: str) -> int:
    """查询用户已领取的分享奖励次数（用于上限检查）。"""
    try:
        result = supabase.table("bonus_events").select("id").eq(
            "user_id", user_id
        ).eq("event_type", "share").execute()
        return len(result.data) if hasattr(result, "data") else 0
    except Exception:
        return 0


def grant_bonus(user_id: str, event_type: str, amount_gb: float, source: str = "") -> bool:
    """发放 bonus 额度（+amount_gb GB），写审计表。返回是否成功。

    防重复：同一 (event_type, source) 只发一次。
    """
    if not user_id:
        return False

    # 防重复：同 source 的事件只发一次
    if source:
        try:
            dup = supabase.table("bonus_events").select("id").eq(
                "user_id", user_id
            ).eq("event_type", event_type).eq("source", source).execute()
            if dup.data:
                return False
        except Exception:
            pass

    # 1. 写审计事件
    event = {
        "user_id": user_id,
        "event_type": event_type,
        "amount_gb": amount_gb,
        "source": source,
        "created_at": _now_iso(),
    }
    if _is_sqlite:
        event["id"] = str(uuid.uuid4())
    try:
        supabase.table("bonus_events").insert(event).execute()
    except Exception as e:
        logger.error("bonus event insert failed: %s", e)
        return False

    # 2. 更新 users.bonus_storage_gb（读-改-写；并发量低，可接受）
    try:
        current = get_bonus_gb(user_id)
        supabase.table("users").update({
            "bonus_storage_gb": current + amount_gb
        }).eq("id", user_id).execute()
    except Exception as e:
        logger.error("bonus update failed: %s", e)
        return False

    logger.info("bonus granted: user=%s type=%s amount=%s source=%s",
                user_id, event_type, amount_gb, source)
    return True


def grant_referral_bonus_on_first_backup(user_id: str) -> None:
    """好友完成首次备份时调用：给邀请人 +1GB（每好友一次，防重复）。

    user_id = 刚完成备份的用户（被邀请人）。该用户需通过 referral 注册
    （referrals.referred_user_id == user_id）。
    """
    try:
        ref = supabase.table("referrals").select(
            "id,referrer_id,reward_granted"
        ).eq("referred_user_id", user_id).execute()
        rows = ref.data if hasattr(ref, "data") else []
        if not rows:
            return  # 不是通过邀请注册
        row = rows[0]
        if row.get("reward_granted"):
            return  # 已发放
        referrer_id = row.get("referrer_id")
        if not referrer_id or referrer_id == user_id:
            return  # 无效或自邀请

        if grant_bonus(referrer_id, "referral", REFERRAL_BONUS_GB, source=str(user_id)):
            try:
                supabase.table("referrals").update({
                    "reward_granted": True
                }).eq("id", row["id"]).execute()
            except Exception as e:
                logger.error("referral reward_granted update failed: %s", e)
    except Exception as e:
        logger.warning("referral bonus grant failed for %s: %s", user_id, e)

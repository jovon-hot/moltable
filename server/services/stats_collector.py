"""Daily statistics collector — aggregates counts into daily_stats table.

Runs periodically (every hour) via the FastAPI startup event.  Each run
checks whether today's row already exists; if not, collects and inserts it.
"""
import os
import logging
import asyncio
from datetime import datetime, timezone, date, timedelta
from typing import Optional

from app_state import supabase

logger = logging.getLogger("moltable.stats_collector")

STATS_ENABLED = os.getenv("MOLTABLE_STATS_ENABLED", "true").lower() in ("1", "true", "yes")


def _count_table(table: str, extra_filter = None) -> int:
    """Count rows in a table, optionally with a WHERE clause."""
    try:
        if extra_filter:
            q = supabase.table(table).select("id", count="exact")
            for clause in extra_filter.split(" AND "):
                parts = clause.split("=", 1)
                if len(parts) == 2:
                    q = q.eq(parts[0].strip(), parts[1].strip())
            result = q.execute()
        else:
            result = supabase.table(table).select("id", count="exact").execute()
        return getattr(result, "count", 0) or 0
    except Exception as e:
        logger.debug("count_table(%s) failed: %s", table, e)
        return 0


def _count_active_users_today() -> int:
    """Count distinct users whose last_active_at falls on today's date.

    Falls back to 0 if the column doesn't exist or the query fails.
    """
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        result = supabase.table("users") \
            .select("id", count="exact") \
            .gte("last_active_at", today + "T00:00:00Z") \
            .execute()
        return getattr(result, "count", 0) or 0
    except Exception:
        return 0


def collect_daily_stats():
    """Collect today's stats and write to daily_stats table.

    Returns the collected data dict, or None if already collected or failed.
    """
    if not STATS_ENABLED:
        return None

    today = date.today()
    today_str = today.isoformat()

    try:
        # Check if today already collected
        existing = supabase.table("daily_stats").select("date").eq("date", today_str).execute()
        if existing.data and len(existing.data) > 0:
            logger.debug("Daily stats for %s already collected", today_str)
            return None
    except Exception:
        # daily_stats table might not exist yet — that's fine
        pass

    # ── Count everything ──────────────────────────
    try:
        total_users = _count_table("users")
        total_memories = _count_table("memories")
        total_projects = _count_table("projects")
        total_personas = _count_table("personas")
        active_users = _count_active_users_today()

        # New users today
        new_today = _count_table("users", f"created_at=gte.{today_str}T00:00:00Z")

        # New users this week
        week_start = (today - timedelta(days=today.weekday())).isoformat()
        new_week = _count_table("users", f"created_at=gte.{week_start}T00:00:00Z")

        # Trial activated users (plan=pro)
        trial_activated = _count_table("users", "plan=pro")

        # API calls today — try to count from a simple table if it exists;
        # for now we use active_users as a proxy, actual API call tracking
        # would need request logging middleware.
        # Placeholder: query audit_logs for today
        api_calls = 0
        error_count = 0

        from app_state import get_error_count
        error_count = get_error_count()

        stats = {
            "date": today_str,
            "total_users": total_users,
            "new_users": new_today,
            "active_users": active_users,
            "api_calls": api_calls,
            "errors": error_count,
            "trial_activated": trial_activated,
        }

        # Write to daily_stats
        supabase.table("daily_stats").insert(stats).execute()
        logger.info("Daily stats collected for %s: %s", today_str, stats)
        return stats

    except Exception as e:
        logger.warning("Failed to collect daily stats: %s", e)
        return None


# ── Scheduled wrapper for startup event ──────────

async def stats_collector_loop():
    """Run collect_daily_stats() every hour (check once per hour)."""
    while True:
        await asyncio.sleep(3600)  # 1 hour
        try:
            collect_daily_stats()
        except Exception as e:
            logger.warning("Stats collector loop error: %s", e)


# ── Realtime stats query (called by admin API) ───

def get_today_stats(db) -> dict:
    """Return realtime stats for the admin dashboard.

    Queries tables directly — does not use the daily_stats cache.
    Parameter 'db' is the Supabase client (for interface compatibility).
    """
    today_str = date.today().isoformat()
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()

    def _count(table: str) -> int:
        try:
            result = supabase.table(table).select("id", count="exact").execute()
            return getattr(result, "count", 0) or 0
        except Exception:
            return 0

    def _count_where(table: str, col: str, op_val: str) -> int:
        try:
            result = supabase.table(table).select("id", count="exact") \
                .gte(col, op_val).execute()
            return getattr(result, "count", 0) or 0
        except Exception:
            return 0

    def _count_eq(table: str, col: str, val: str) -> int:
        try:
            result = supabase.table(table).select("id", count="exact") \
                .eq(col, val).execute()
            return getattr(result, "count", 0) or 0
        except Exception:
            return 0

    from app_state import get_error_count

    return {
        "total_users": _count("users"),
        "new_users_today": _count_where("users", "created_at", today_str + "T00:00:00Z"),
        "new_users_week": _count_where("users", "created_at", week_start + "T00:00:00Z"),
        "active_users_today": _count_where("users", "last_active_at", today_str),
        "trial_activated": _count_eq("users", "plan", "pro"),
        "trial_active": _count_eq("users", "plan", "pro"),  # same as trial_activated for now
        "total_memories": _count("memories"),
        "total_projects": _count("projects"),
        "total_personas": _count("personas"),
        "api_calls_today": _count_where("audit_logs", "created_at", today_str + "T00:00:00Z"),
    }

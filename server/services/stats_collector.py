"""Daily stats collector — lightweight aggregation for admin dashboard.

Runs every hour.  Does NOT depend on daily_stats table (created separately
in Supabase SQL editor).  All queries handle missing columns gracefully.
"""
import os
import logging
import asyncio
from datetime import datetime, timezone, date, timedelta

from typing import Optional

from app_state import supabase

logger = logging.getLogger("moltable.stats_collector")

STATS_ENABLED = os.getenv("MOLTABLE_STATS_ENABLED", "true").lower() in ("1", "true", "yes")


def _safe_count(table: str, **filters) -> int:
    """Count rows with optional equality filters.  Returns 0 on any error."""
    try:
        q = supabase.table(table).select("id", count="exact")
        for col, val in filters.items():
            q = q.eq(col, val)
        result = q.execute()
        return getattr(result, "count", 0) or 0
    except Exception:
        return 0


def _safe_gte_count(table: str, col: str, val: str) -> int:
    """Count rows WHERE col >= val.  Returns 0 on any error (missing col, etc)."""
    try:
        result = supabase.table(table).select("id", count="exact").gte(col, val).execute()
        return getattr(result, "count", 0) or 0
    except Exception:
        return 0


def collect_daily_stats() -> Optional[dict]:
    """Collect today's platform stats.  Logs the result; does NOT persist to DB.

    Use GET /api/admin/stats for the realtime dashboard (calls get_today_stats).
    """
    if not STATS_ENABLED or supabase is None:
        return None

    today = date.today().isoformat()
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()

    try:
        total_users = _safe_count("users")
        total_memories = _safe_count("memories")
        total_projects = _safe_count("projects")
        total_personas = _safe_count("personas")
        trial = _safe_count("users", plan="pro")
        new_today = _safe_gte_count("users", "created_at", today)
        new_week = _safe_gte_count("users", "created_at", week_start)
        active_today = _safe_gte_count("users", "last_active_at", today)

        from app_state import get_error_count

        stats = {
            "date": today,
            "total_users": total_users,
            "new_users": new_today,
            "new_users_week": new_week,
            "active_users": active_today,
            "trial_activated": trial,
            "trial_active": trial,
            "total_memories": total_memories,
            "total_projects": total_projects,
            "total_personas": total_personas,
            "errors": get_error_count(),
        }
        logger.info("Daily stats for %s: users=%d (+%d) active=%d trial=%d",
                    today, total_users, new_today, active_today, trial)
        return stats
    except Exception as e:
        logger.warning("Daily stats collection failed: %s", e)
        return None


async def stats_collector_loop():
    """Run collect_daily_stats() every hour."""
    while True:
        await asyncio.sleep(3600)
        try:
            collect_daily_stats()
        except Exception as e:
            logger.warning("Stats loop error: %s", e)


# ── Realtime stats (called by admin API) ──────────────────

def get_today_stats(_db=None) -> dict:
    """Return realtime stats for the admin dashboard."""
    today = date.today().isoformat()
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()

    from app_state import get_error_count

    return {
        "total_users": _safe_count("users"),
        "new_users_today": _safe_gte_count("users", "created_at", today),
        "new_users_week": _safe_gte_count("users", "created_at", week_start),
        "active_users_today": _safe_gte_count("users", "last_active_at", today),
        "trial_activated": _safe_count("users", plan="pro"),
        "trial_active": _safe_count("users", plan="pro"),
        "total_memories": _safe_count("memories"),
        "total_projects": _safe_count("projects"),
        "total_personas": _safe_count("personas"),
        "api_calls_today": 0,
    }

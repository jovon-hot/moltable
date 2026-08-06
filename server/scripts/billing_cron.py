#!/usr/bin/env python3
"""
Moltable Billing Downgrade Cron
Daily: Check for expired trials → downgrade to free plan → notify user.

Works in two modes:
  1. SQLite direct (local dev) — when no MOLTABLE_API_URL set
  2. API mode (production) — when MOLTABLE_API_URL + MOLTABLE_ADMIN_KEY set

Usage:
    python3 billing_cron.py                # check and downgrade
    python3 billing_cron.py --dry-run      # check only, no writes
    python3 billing_cron.py --notify       # also send notification
"""

import os, sys, json, sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Config ──────────────────────────────────────────────
API_BASE = os.getenv("MOLTABLE_API_URL", "")
ADMIN_KEY = os.getenv("MOLTABLE_ADMIN_KEY", "")
DB_PATH = os.getenv(
    "MOLTABLE_DB_PATH",
    str(Path(__file__).resolve().parent.parent / "moltable_dev.db")
)
TRIAL_DAYS = 90
WARN_DAYS = 7  # warn when ≤ 7 days left
DRY_RUN = "--dry-run" in sys.argv
NOTIFY = "--notify" in sys.argv
USE_API = bool(API_BASE and ADMIN_KEY)

now = datetime.now(timezone.utc)


# ═══════════════════════════════════════════════════
#  SQLite mode
# ═══════════════════════════════════════════════════

def sqlite_get_users(db_path: str) -> list[dict]:
    """Get all users who are NOT on free plan."""
    if not os.path.exists(db_path):
        print(f"  DB not found: {db_path}")
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, email, name, plan, created_at FROM users WHERE plan != 'free'"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def sqlite_downgrade(db_path: str, user_id: str) -> bool:
    """Downgrade a user to free plan."""
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE users SET plan = 'free' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True


# ═══════════════════════════════════════════════════
#  API mode
# ═══════════════════════════════════════════════════

def api_call(method, path, body=None):
    import urllib.request, urllib.error
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Admin-Key", ADMIN_KEY)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:200]}
    except Exception as e:
        return {"error": str(e)}


def api_get_users() -> tuple[list[dict], str | None]:
    resp = api_call("GET", "/api/admin/users?plan=pro,team")
    if "error" in resp:
        return [], resp["error"]
    return resp.get("users", resp.get("data", [])), None


def api_downgrade(user_id: str):
    return api_call("POST", f"/api/admin/users/{user_id}/downgrade", {
        "plan": "free",
        "reason": "trial_expired",
    })


def api_notify(user_id: str, email: str, notif_type: str, days_left: int = 0):
    return api_call("POST", "/api/admin/notify", {
        "user_id": user_id,
        "email": email,
        "type": notif_type,
        "days_left": days_left,
    })


# ═══════════════════════════════════════════════════
#  Core logic
# ═══════════════════════════════════════════════════

def process_users(users: list[dict]) -> dict:
    downgraded, warned, active = 0, 0, 0

    for user in users:
        user_id = user.get("id", "")
        email = user.get("email", "unknown")
        plan = user.get("plan", "free")

        # Determine trial start
        trial_start = user.get("trial_started_at") or user.get("created_at")
        if not trial_start:
            continue

        try:
            started = datetime.fromisoformat(str(trial_start).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue

        expires = started + timedelta(days=TRIAL_DAYS)
        days_left = (expires - now).days

        # Expired → downgrade
        if days_left < 0:
            print(f"  ✗  {email:<30} trial expired ({abs(days_left)}d ago) → downgrading to free")
            if not DRY_RUN:
                success = False
                if USE_API:
                    result = api_downgrade(user_id)
                    success = "error" not in result
                else:
                    success = sqlite_downgrade(DB_PATH, user_id)
                if success:
                    downgraded += 1
                if NOTIFY and USE_API:
                    api_notify(user_id, email, "trial_expired")
            else:
                downgraded += 1  # count as would-downgrade in dry-run
            continue

        # Warning period
        if days_left <= WARN_DAYS:
            print(f"  ⚠  {email:<30} {plan} · {days_left}d left — warning")
            warned += 1
            if not DRY_RUN and NOTIFY and USE_API:
                api_notify(user_id, email, "trial_expiring", days_left)
            continue

        # Active
        print(f"  ✓  {email:<30} {plan} · {days_left}d remaining")
        active += 1

    return {"downgraded": downgraded, "warned": warned, "active": active}


# ═══════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════

def main():
    print(f"Moltable Billing Cron — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Mode: {'API → ' + API_BASE if USE_API else 'SQLite → ' + DB_PATH}")
    print(f"{'DRY RUN — no writes' if DRY_RUN else 'LIVE MODE'}")
    print()

    # Fetch users
    if USE_API:
        users, err = api_get_users()
        if err:
            print(f"Failed to fetch users: {err}")
            return 1
    else:
        users = sqlite_get_users(DB_PATH)

    if not users:
        print("No trial users found (all users on free plan)")
        return 0

    # Process
    result = process_users(users)
    total = result["downgraded"] + result["warned"] + result["active"]
    print(f"\nSummary: {result['downgraded']} downgraded, {result['warned']} warned, "
          f"{result['active']} active, {total} checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())

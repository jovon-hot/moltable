#!/usr/bin/env python3
"""
billing_cron.py — Trial expiration cron job

Scans for users whose 90-day free trial has expired and downgrades them
from pro/team → free. Safe to run repeatedly (idempotent).

Usage:
    python scripts/billing_cron.py          # dry-run (report only)
    python scripts/billing_cron.py --apply  # actually downgrade

Schedule: daily via cron or Hermes cron job.
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime, timedelta, timezone

# ── Path setup ──────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SERVER_DIR)

from repositories.sqlite_adapter import DB_PATH
from dotenv import load_dotenv
load_dotenv()

# ── Config ──────────────────────────────────────────────
TRIAL_DAYS = int(os.getenv("MOLTABLE_TRIAL_DAYS", "90"))
DRY_RUN = "--apply" not in sys.argv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("billing_cron")


def main():
    mode = "DRY RUN" if DRY_RUN else "APPLY"
    logger.info("=" * 60)
    logger.info("Billing Cron — Trial Expiration Check (%s)", mode)
    logger.info("Trial duration: %d days", TRIAL_DAYS)
    logger.info("=" * 60)

    if not os.path.exists(DB_PATH):
        logger.error("Database not found: %s", DB_PATH)
        return 1

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # 1. Find trial users (pro/team with trial_activated_at set)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, name, plan, trial_activated_at, created_at
        FROM users
        WHERE plan IN ('pro', 'team')
          AND trial_activated_at IS NOT NULL
    """)
    trial_users = cursor.fetchall()

    if not trial_users:
        logger.info("No active trial users found. Nothing to do.")
        conn.close()
        return 0

    logger.info("Found %d trial user(s)", len(trial_users))

    # 2. Check each for expiration
    now = datetime.now(timezone.utc)
    expired = []
    still_active = []
    no_trial_date = []

    for user in trial_users:
        user_id = user["id"]
        email = user["email"] or "(no email)"
        plan = user["plan"]
        trial_at_str = user["trial_activated_at"]
        created_at = user["created_at"]

        if not trial_at_str:
            # Fallback: use created_at if trial_activated_at was never set
            # (legacy users who activated before the fix)
            if created_at:
                trial_date = datetime.fromisoformat(created_at)
                no_trial_date.append((user_id, email, plan, trial_date.isoformat()))
            else:
                logger.warning("  SKIP: user %s has no trial_activated_at or created_at", user_id)
                continue
        else:
            trial_date = datetime.fromisoformat(trial_at_str)

        expires_at = trial_date + timedelta(days=TRIAL_DAYS)

        # Ensure timezone-aware comparison
        if trial_date.tzinfo is None:
            trial_date = trial_date.replace(tzinfo=timezone.utc)
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if now > expires_at:
            expired.append({
                "id": user_id,
                "email": email,
                "plan": plan,
                "trial_started": trial_date.isoformat(),
                "expired_at": expires_at.isoformat(),
                "days_overdue": (now - expires_at).days,
                "source": "trial_activated_at" if trial_at_str else "created_at (fallback)",
            })
        else:
            days_left = (expires_at - now).days
            still_active.append({
                "id": user_id,
                "email": email,
                "plan": plan,
                "trial_started": trial_date.isoformat(),
                "expires_at": expires_at.isoformat(),
                "days_left": days_left,
            })

    # 3. Report active trials
    if still_active:
        logger.info("--- Active Trials (%d) ---", len(still_active))
        for u in still_active:
            logger.info(
                "  %s | %s | %s | expires %s (%d days left)",
                u["id"], u["email"], u["plan"], u["expires_at"][:10], u["days_left"]
            )

    # 4. Handle expired trials
    if no_trial_date:
        logger.info("--- Using created_at as fallback (%d) ---", len(no_trial_date))
        for u in no_trial_date:
            logger.info("  %s | %s | %s | created %s", u[0], u[1], u[2], u[3])

    if expired:
        logger.warning("--- EXPIRED Trials (%d) ---", len(expired))
        for u in expired:
            logger.warning(
                "  %s | %s | %s | expired %s (%d days overdue) | source: %s",
                u["id"], u["email"], u["plan"],
                u["expired_at"][:10], u["days_overdue"], u["source"],
            )

        if not DRY_RUN:
            # 5. Downgrade expired users
            for u in expired:
                try:
                    conn.execute(
                        "UPDATE users SET plan = 'free' WHERE id = ?",
                        (u["id"],)
                    )
                    conn.commit()
                    logger.info(
                        "  DOWNGRADED: %s (%s) %s → free",
                        u["id"], u["email"], u["plan"]
                    )
                except Exception as e:
                    logger.error("  FAILED to downgrade %s: %s", u["id"], e)
        else:
            logger.info(
                "DRY RUN — add --apply to actually downgrade %d user(s)", len(expired)
            )
    else:
        logger.info("No expired trials found.")

    # 6. Summary
    logger.info("--- Summary ---")
    logger.info("Total trial users checked: %d", len(trial_users))
    logger.info("Still active: %d", len(still_active))
    logger.info("Expired (would downgrade): %d", len(expired))
    logger.info("Mode: %s", mode)

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

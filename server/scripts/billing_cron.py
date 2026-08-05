#!/usr/bin/env python3
"""
Moltable Billing Downgrade Cron
Daily: Check for expired trials → downgrade to free plan → notify user.

Usage:
    python3 billing_cron.py                # check and downgrade
    python3 billing_cron.py --dry-run      # check only, no writes
    python3 billing_cron.py --notify       # also send email (needs RESEND_API_KEY)
"""

import os, sys, json
from datetime import datetime, timezone, timedelta
import urllib.request
import urllib.error

API_BASE = os.getenv("MOLTABLE_API_URL", "https://api.moltable.ai")
ADMIN_KEY = os.getenv("MOLTABLE_ADMIN_KEY", "")
DRY_RUN = "--dry-run" in sys.argv
NOTIFY = "--notify" in sys.argv

def api_call(method, path, body=None):
    """Simple REST call to Moltable API"""
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if ADMIN_KEY:
        req.add_header("X-Admin-Key", ADMIN_KEY)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:200]}
    except Exception as e:
        return {"error": str(e)}

def main():
    now = datetime.now(timezone.utc)
    print(f"Moltable Billing Cron — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'DRY RUN — no writes' if DRY_RUN else 'LIVE MODE'}")
    print()

    # 1. List users with active trials (plan = pro/team, not free)
    resp = api_call("GET", "/api/admin/users?plan=pro,team")
    if "error" in resp:
        print(f"Failed to fetch users: {resp['error']}")
        return 1

    users = resp.get("users", resp.get("data", []))
    if not users:
        print("No trial users found")
        return 0

    downgraded = 0
    warned = 0

    for user in users:
        if not isinstance(user, dict):
            continue
        user_id = user.get("id", "")
        email = user.get("email", "")
        plan = user.get("plan", "")
        
        # Check trial expiry
        trial_start = user.get("trial_started_at") or user.get("created_at")
        if not trial_start:
            continue
        
        try:
            started = datetime.fromisoformat(trial_start.replace("Z", "+00:00"))
        except:
            continue
        
        expires = started + timedelta(days=90)
        days_left = (expires - now).days
        
        # 7-day warning
        if 0 <= days_left <= 7 and not DRY_RUN:
            if NOTIFY:
                api_call("POST", "/api/admin/notify", {
                    "user_id": user_id,
                    "email": email,
                    "type": "trial_expiring",
                    "days_left": days_left,
                })
            warned += 1
            print(f"  ⚠  {email}: {days_left}d left — warning sent")
            continue
        
        # Expired → downgrade
        if days_left < 0:
            print(f"  ✗  {email}: trial expired ({abs(days_left)}d ago) → downgrading to free")
            if not DRY_RUN:
                result = api_call("POST", f"/api/admin/users/{user_id}/downgrade", {
                    "plan": "free",
                    "reason": "trial_expired",
                })
                if "error" not in result:
                    downgraded += 1
                if NOTIFY:
                    api_call("POST", "/api/admin/notify", {
                        "user_id": user_id,
                        "email": email,
                        "type": "trial_expired",
                    })
        else:
            print(f"  ✓  {email}: {plan} · {days_left}d remaining")

    print(f"\nSummary: {downgraded} downgraded, {warned} warned, {len(users)} checked")
    return 0

if __name__ == "__main__":
    sys.exit(main())

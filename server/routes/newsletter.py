"""Newsletter subscription route — stores subscribers and sends welcome emails."""

import json
import logging
import os
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

logger = logging.getLogger("moltable.newsletter")

router = APIRouter(prefix="/api/newsletter", tags=["newsletter"])

# ── Storage ──────────────────────────────────────────────
SUBSCRIBERS_FILE = Path(__file__).resolve().parent.parent / "data" / "newsletter_subscribers.json"


def _load_subscribers() -> list[dict]:
    """Load subscribers from JSON file."""
    if not SUBSCRIBERS_FILE.exists():
        return []
    try:
        with open(SUBSCRIBERS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_subscribers(subscribers: list[dict]) -> None:
    """Save subscribers to JSON file."""
    SUBSCRIBERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subscribers, f, indent=2, ensure_ascii=False, default=str)


# ── Models ───────────────────────────────────────────────
class SubscribeRequest(BaseModel):
    email: str
    source: str = "blog"  # blog, landing, github, etc.


class SubscribeResponse(BaseModel):
    ok: bool
    message: str
    count: int


# ── Endpoints ────────────────────────────────────────────

@router.post("/subscribe", response_model=SubscribeResponse)
async def subscribe(req: SubscribeRequest):
    """Subscribe an email to the newsletter."""
    email = req.email.strip().lower()

    # Basic validation
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    if len(email) > 254:
        raise HTTPException(status_code=400, detail="Email too long")

    subscribers = _load_subscribers()

    # Check for duplicates
    for sub in subscribers:
        if sub.get("email") == email:
            return SubscribeResponse(
                ok=True,
                message="You're already subscribed! 🎉",
                count=len(subscribers),
            )

    # Add subscriber
    from datetime import datetime, timezone

    subscribers.append({
        "email": email,
        "source": req.source,
        "subscribed_at": datetime.now(timezone.utc).isoformat(),
        "confirmed": False,
    })

    _save_subscribers(subscribers)

    # Try to send welcome email
    try:
        from email_utils import send_email_sync
        welcome_html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0D0D14;color:#F5F4F8;padding:40px 20px">
<div style="max-width:480px;margin:0 auto;background:#14141E;border-radius:12px;padding:32px;border:1px solid rgba(99,102,241,0.15)">
  <div style="text-align:center;margin-bottom:24px"><span style="font-size:32px">🧬</span></div>
  <h1 style="font-size:20px;font-weight:700;text-align:center;margin-bottom:12px">
    Welcome to the Moltable Newsletter
  </h1>
  <p style="font-size:14px;line-height:1.7;color:#85829E;margin-bottom:20px">
    Thanks for subscribing! You'll receive weekly deep-dives on AI Identity, MCP protocol, and agent infrastructure — straight to your inbox.
  </p>
  <p style="font-size:13px;color:#A8A5B8;margin-bottom:20px">
    In the meantime, check out our latest content:
  </p>
  <p style="margin-bottom:8px">
    <a href="https://www.moltable.ai/blog/moltable-vs-mem0-identity-vs-memory" style="color:#6366F1;font-size:13px;text-decoration:none">
      → Moltable vs mem0: Identity Layer vs Memory Layer
    </a>
  </p>
  <p style="margin-bottom:8px">
    <a href="https://www.moltable.ai/blog/rag-vs-finetuning-vs-identity" style="color:#6366F1;font-size:13px;text-decoration:none">
      → RAG vs Fine-Tuning vs Identity Layer
    </a>
  </p>
  <p style="margin-bottom:24px">
    <a href="https://www.moltable.ai/blog/three-minute-env-recovery" style="color:#6366F1;font-size:13px;text-decoration:none">
      → 3-Minute Full AI Dev Environment Recovery
    </a>
  </p>
  <p style="font-size:12px;color:#6E6B80;text-align:center">
    — The Moltable Team<br>
    <a href="https://moltable.ai" style="color:#6366F1">moltable.ai</a>
  </p>
</div>
</body>
</html>"""
        send_email_sync(email, "Welcome to the Moltable Newsletter 🧬", welcome_html, welcome_html)
    except Exception as e:
        logger.warning(f"Welcome email failed for {email}: {e}")

    logger.info(f"New newsletter subscriber: {email} (source: {req.source})")
    return SubscribeResponse(
        ok=True,
        message="Successfully subscribed! Check your inbox. 📬",
        count=len(subscribers),
    )


@router.get("/count")
async def subscriber_count():
    """Get total subscriber count (public endpoint for social proof)."""
    subscribers = _load_subscribers()
    confirmed = sum(1 for s in subscribers if s.get("confirmed"))
    return {
        "total": len(subscribers),
        "confirmed": confirmed,
    }

"""Email utilities — Resend provider.

Free tier: 100 emails/day. Sign up at https://resend.com → API Keys → copy key.
Set env: RESEND_API_KEY=re_xxxxxxxx

Fallback: logs to console when no key configured.
"""
import logging
import os

import httpx

logger = logging.getLogger("moltable.email")

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("EMAIL_FROM", "Moltable <noreply@moltable.ai>")
BASE_URL = "https://api.resend.com"


async def send_email(to: str, subject: str, html: str, text: str = "") -> bool:
    """Send email via Resend. Returns True on success."""
    if not RESEND_API_KEY:
        logger.info(f"[EMAIL-DRY-RUN] To: {to} | Subject: {subject}")
        logger.debug(f"[EMAIL-DRY-RUN] Body: {html[:200]}...")
        return False  # not an error, just not configured

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{BASE_URL}/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": FROM_EMAIL,
                    "to": [to],
                    "subject": subject,
                    "html": html,
                    "text": text or html,
                },
            )
            if resp.status_code == 200:
                logger.info(f"Email sent: {to} — {subject}")
                return True
            else:
                logger.error(f"Resend error {resp.status_code}: {resp.text[:200]}")
                return False
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False


def send_email_sync(to: str, subject: str, html: str, text: str = "") -> bool:
    """Synchronous wrapper for non-async contexts."""
    if not RESEND_API_KEY:
        logger.info(f"[EMAIL-DRY-RUN] To: {to} | Subject: {subject}")
        return False

    import requests
    try:
        resp = requests.post(
            f"{BASE_URL}/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": FROM_EMAIL,
                "to": [to],
                "subject": subject,
                "html": html,
                "text": text or html,
            },
            timeout=15,
        )
        if resp.status_code == 200:
            logger.info(f"Email sent: {to} — {subject}")
            return True
        else:
            logger.error(f"Resend error {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False


# ---- Templates ----

VERIFY_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background:#08090a; color:#f7f8f8; padding:40px 20px;">
<div style="max-width:480px; margin:0 auto; background:#0f1011; border-radius:12px; padding:32px; box-shadow:0 0 0 1px rgba(255,255,255,0.06);">
  <div style="text-align:center; margin-bottom:24px;">
    <svg width="40" height="40" viewBox="0 0 200 200" fill="none"><circle cx="100" cy="100" r="60" stroke="#7170ff" stroke-width="4"/><circle cx="100" cy="100" r="15" fill="#7170ff"/><circle cx="160" cy="100" r="12" stroke="#7170ff" stroke-width="3"/><circle cx="40" cy="100" r="12" stroke="#7170ff" stroke-width="3"/></svg>
  </div>
  <h1 style="font-size:20px; font-weight:600; text-align:center; margin-bottom:12px; color:#f7f8f8;">Verify your email 📬</h1>

  <p style="font-size:14px; line-height:1.7; color:#8a8f98; margin-bottom:24px;">
    Confirm your email address to activate your Moltable account and start backing up your Agent soul.
  </p>

  <a href="{verify_url}" style="display:block; text-align:center; background:#7170ff; color:#fff; padding:12px 24px; border-radius:8px; text-decoration:none; font-size:14px; font-weight:510;">Verify Email →</a>

  <p style="font-size:12px; color:#5a5f68; margin-top:20px; word-break:break-all;">
    Or paste this link in your browser:<br>
    <code style="color:#7170ff;">{verify_url}</code>
  </p>

  <p style="font-size:11px; color:#5a5f68; text-align:center; margin-top:24px;">
    This link expires in 30 minutes · moltable.ai · Your AI, always in sync
  </p>
</div>
</body>
</html>"""

VERIFY_TEXT = """Verify your email — Moltable 📬

Confirm your email address to activate your Moltable account:

{verify_url}

This link expires in 30 minutes.

moltable.ai · Your AI, always in sync
"""


def send_verification_email(email: str, token: str) -> bool:
    """Send email verification link to user."""
    verify_url = f"https://api.moltable.ai/api/auth/verify-email?token={token}"
    html = VERIFY_HTML.format(verify_url=verify_url)
    text = VERIFY_TEXT.format(verify_url=verify_url)
    return send_email_sync(email, "Verify your email — Moltable", html, text)

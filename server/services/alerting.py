"""Alerting via webhook (WeCom/钉钉/Discord/Slack).

Configure ALERT_WEBHOOK_URL in environment.  Alerts are fire-and-forget
and never block the main request path.
"""
import os
import json
import logging
import threading
from urllib.request import Request, urlopen
from urllib.error import URLError

logger = logging.getLogger("moltable.alerting")

ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "")
ALERT_ERROR_THRESHOLD = int(os.getenv("ALERT_ERROR_THRESHOLD", "5"))
ALERT_WINDOW_MINUTES = int(os.getenv("ALERT_WINDOW_MINUTES", "5"))

_alert_enabled = bool(ALERT_WEBHOOK_URL)
_cooldown_lock = threading.Lock()
_last_alert_time: float = 0.0
_ALERT_COOLDOWN_SECONDS = 300  # 5 min between alerts


def is_alert_enabled() -> bool:
    return _alert_enabled


def _post_webhook(message: str) -> bool:
    """POST a text message to the webhook URL.  Non-blocking helper."""
    payload = json.dumps({
        "msgtype": "text",
        "text": {"content": message},
    }).encode("utf-8")

    req = Request(
        ALERT_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(req, timeout=5) as resp:
            return 200 <= resp.status < 300
    except URLError as e:
        logger.warning("Alert webhook POST failed: %s", e)
        return False


def send_alert(message: str) -> bool:
    """Send an alert to the configured webhook.

    Rate-limited: at most one alert every 5 minutes (cooldown).
    Never raises — failures are logged and swallowed.

    Returns True if the alert was actually sent.
    """
    if not _alert_enabled:
        return False

    global _last_alert_time
    now = __import__("time").time()

    with _cooldown_lock:
        if now - _last_alert_time < _ALERT_COOLDOWN_SECONDS:
            logger.debug("Alert suppressed (cooldown): %s", message)
            return False
        _last_alert_time = now

    # Fire in background thread so we never block the caller
    def _send():
        try:
            _post_webhook(message)
        except Exception as exc:
            logger.warning("Alert send failed: %s", exc)

    threading.Thread(target=_send, daemon=True).start()
    return True


def check_and_alert() -> None:
    """Check error count and trigger alert if threshold exceeded.

    Call this from the global exception handler.
    This is the main entry point used by main.py.
    """
    if not _alert_enabled:
        return

    from app_state import get_error_count
    error_count = get_error_count()

    if error_count >= ALERT_ERROR_THRESHOLD:
        msg = (
            f"[Moltable] 异常告警: "
            f"过去{ALERT_WINDOW_MINUTES}分钟 {error_count} 次 500 错误"
        )
        send_alert(msg)


# Alias for backward compatibility
check_error_alert = check_and_alert

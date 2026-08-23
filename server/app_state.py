"""Shared app state — avoids circular imports between main.py and route modules."""
import logging
import os

from dotenv import load_dotenv

load_dotenv()

from slowapi import Limiter
from slowapi.util import get_remote_address

# supabase 包是可选的——未安装时用 SQLite
try:
    from supabase import Client, create_client
    _has_supabase = True
except ImportError:
    _has_supabase = False
    Client = None

logger = logging.getLogger("moltable")

# ── Rate Limiter ──────────────────────────────────────────
def client_ip(request) -> str:
    """提取真实客户端 IP。

    Railway 等反向代理把真实 IP 放在 X-Forwarded-For 首位，而 request.client.host
    是内部代理 IP（100.64.x.x）且每次请求都变化，直接用它会导致 IP 限流/追踪/审计失效。
    """
    if request is not None and getattr(request, "headers", None):
        xff = request.headers.get("x-forwarded-for", "")
        if xff:
            return xff.split(",")[0].strip()
    return request.client.host if request and request.client else "unknown"


def _client_ip_key(request):
    return client_ip(request)


limiter = Limiter(key_func=_client_ip_key)

# ── Supabase ──────────────────────────────────────────────
# 🔒 Security: prefer SUPABASE_ANON_KEY + RLS over service_role key.
# Using service_role key bypasses Row Level Security — user data isolation
# relies entirely on application-level .eq("user_id", ...) filters.
# Set SUPABASE_ANON_KEY to enable RLS enforcement.
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
if _has_supabase and supabase_url and supabase_key:
    supabase: Client = create_client(supabase_url, supabase_key)
    _is_sqlite = False
    logger.info("已连接 Supabase: %s", supabase_url)
else:
    logger.info("SUPABASE_URL 未设置或 supabase 包未安装 — 使用 SQLite 本地数据库")
    from repositories.sqlite_adapter import SQLiteClient, init_schema
    _sqlite_client = SQLiteClient()
    init_schema(_sqlite_client)
    supabase = _sqlite_client
    _is_sqlite = True  # flag for get_store()

# ── Vector Store (lazy-init to avoid circular imports) ────
_store = None

def get_store():
    global _store
    if _store is None:
        from repositories.memory_repo import SupabaseMemoryRepository
        from services.vector_store import VectorStore
        # SQLite mode: no in-memory VectorStore fallback; the repo handles its own
        _fallback = None if _is_sqlite else VectorStore()
        _store = SupabaseMemoryRepository(supabase, fallback_store=_fallback)
    return _store

# ── Allowed Origins (reusable) ───────────────────────────
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:8701,http://localhost:3000,https://moltable.ai,https://www.moltable.ai")
# Always include production domains (env var might not have them from older deploys)
_production_domains = ["https://moltable.ai", "https://www.moltable.ai"]
_raw_origins = [o.strip() for o in ALLOWED_ORIGINS_STR.split(",") if o.strip()]
allowed_origins = list(dict.fromkeys(_raw_origins + _production_domains))  # dedupe-preserving order

# ── Persona Version (incremented on any change; Agent compares to detect drift) ──
_persona_version = 0


def bump_persona_version():
    global _persona_version
    _persona_version += 1
    return _persona_version


def get_persona_version() -> int:
    return _persona_version


# ── Error Monitoring (纯本地，不依赖 Sentry 等外部服务) ───
import threading
import time as _time
from collections import deque

_error_events = deque()        # (timestamp, error_type)
_error_lock = threading.Lock()
_ERROR_WINDOW_SECONDS = 3600   # 1 小时


def record_error(error_type: str = "unknown"):
    """记录一次错误事件（线程安全）。"""
    now = _time.time()
    with _error_lock:
        _error_events.append((now, error_type))
        # 定期清理过期事件
        cutoff = now - _ERROR_WINDOW_SECONDS
        while _error_events and _error_events[0][0] < cutoff:
            _error_events.popleft()


def get_error_count() -> int:
    """返回最近 1 小时内的错误计数。"""
    now = _time.time()
    with _error_lock:
        cutoff = now - _ERROR_WINDOW_SECONDS
        while _error_events and _error_events[0][0] < cutoff:
            _error_events.popleft()
        return len(_error_events)

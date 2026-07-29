"""Shared app state — avoids circular imports between main.py and route modules."""
import logging
import os
from dotenv import load_dotenv
load_dotenv()

from slowapi import Limiter
from slowapi.util import get_remote_address

# supabase 包是可选的——未安装时用 SQLite
try:
    from supabase import create_client, Client
    _has_supabase = True
except ImportError:
    _has_supabase = False
    Client = None

logger = logging.getLogger("moltable")

# ── Rate Limiter ──────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

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
        from services.vector_store import VectorStore
        from repositories.memory_repo import SupabaseMemoryRepository
        # SQLite mode: no in-memory VectorStore fallback; the repo handles its own
        _fallback = None if _is_sqlite else VectorStore()
        _store = SupabaseMemoryRepository(supabase, fallback_store=_fallback)
    return _store

# ── Allowed Origins (reusable) ───────────────────────────
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:8701,http://localhost:3000")
allowed_origins = [o.strip() for o in ALLOWED_ORIGINS_STR.split(",") if o.strip()]

# ── Persona Version (incremented on any change; Agent compares to detect drift) ──
_persona_version = 0


def bump_persona_version():
    global _persona_version
    _persona_version += 1
    return _persona_version


def get_persona_version() -> int:
    return _persona_version

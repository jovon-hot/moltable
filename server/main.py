"""Moltable API Server — AI Identity Layer
FastAPI + Supabase + MCP + DeepSeek LLM
"""
import logging
import os
import signal
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("moltable")

# ── Shared state (avoids circular imports) ────────────────
from app_state import supabase, limiter, allowed_origins, get_store

# ── DeepSeek ──────────────────────────────────────────────
deepseek_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_client = None
if deepseek_key:
    from openai import OpenAI
    deepseek_client = OpenAI(
        api_key=deepseek_key,
        base_url="https://api.deepseek.com/v1"
    )
else:
    logger.warning("DEEPSEEK_API_KEY missing — LLM features disabled")

# ── FastAPI App ───────────────────────────────────────────
app = FastAPI(
    title="Moltable — AI Identity Layer",
    version="0.1.0",
    description="Cross-AI identity system: Identity → Persona → Agent"
)

# ── Security Headers Middleware ───────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://moltable-production-15ad.up.railway.app https://wjkyoqbjcxqqsruuutvf.supabase.co; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

# ── CORS ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Session-Token"],
)

# ── Rate Limiting Handler ─────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Version header middleware ────────────────────────────
@app.middleware("http")
async def add_api_version_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-API-Version"] = "1"
    return response

# ── 1MB Request Body Size Limit Middleware ──────────────
@app.middleware("http")
async def limit_request_body_size(request: Request, call_next):
    """Reject requests with Content-Length > 1MB (1_048_576 bytes)."""
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > 1_048_576:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large — max 1MB"},
                )
        except (ValueError, TypeError):
            pass
    response = await call_next(request)
    return response

# ── Routes ────────────────────────────────────────────────
from routes import memories, provision, personas, auth, mcp, sessions, billing, v1, agents, projects
app.include_router(memories.router)
app.include_router(provision.router)
app.include_router(personas.router)
app.include_router(auth.router)
app.include_router(mcp.router)
app.include_router(sessions.router)
app.include_router(billing.router)
app.include_router(v1.router)
app.include_router(agents.router)
app.include_router(projects.router)
app.add_api_route("/.well-known/mcp", mcp.mcp_discovery, methods=["GET"], tags=["mcp"])


@app.get("/")
async def root(request: Request):
    return {
        "name": "Moltable",
        "version": "0.1.0",
        "status": "running",
        "db": supabase is not None,
        "llm": deepseek_client is not None,
        "vector_store": "supabase+pgvector" if supabase is not None else "in-memory",
    }


@app.get("/health")
async def health(request: Request):
    db_ok = False
    if supabase is not None:
        try:
            supabase.table("users").select("id", count="exact").limit(1).execute()
            db_ok = True
        except Exception:
            pass
    return {
        "status": "ok" if (db_ok or supabase is None) else "degraded",
        "db": db_ok,
        "db_required": supabase is not None,
    }


# ── Startup ───────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8700"))

    def shutdown(sig, frame):
        logger.info("Shutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    logger.info("Starting Moltable on http://0.0.0.0:%d", port)
    logger.info("Allowed origins: %s", allowed_origins)
    uvicorn.run(app, host="0.0.0.0", port=port)

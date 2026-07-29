FROM python:3.11-slim

WORKDIR /app

# ── Install system deps ──────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python deps ─────────────────────────────────────
# Install torch+cpu first to avoid pulling CUDA (~2GB savings on Railway)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── App code ────────────────────────────────────────
COPY . .

# ── Non-root user ───────────────────────────────────
RUN useradd --create-home --shell /bin/bash moltable
RUN chown -R moltable:moltable /app
USER moltable

# ── API Server ──────────────────────────────────────
# Railway injects $PORT; fallback to 8000 for plain Docker
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

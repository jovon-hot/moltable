FROM python:3.11-slim

WORKDIR /app

# ── Install system deps ──────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python deps ─────────────────────────────────────
COPY requirements-railway.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ── App code ────────────────────────────────────────
COPY . .

# ── Non-root user ───────────────────────────────────
RUN useradd --create-home --shell /bin/bash moltable
RUN chown -R moltable:moltable /app
USER moltable

# ── API Server ──────────────────────────────────────
# Railway 注入 $PORT
EXPOSE 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

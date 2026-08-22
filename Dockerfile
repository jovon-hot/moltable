# Dockerfile — Moltable API (FastAPI)
# Railway deployment: Python backend only (frontend is on Vercel)

FROM python:3.11-slim

WORKDIR /app

# ── 精简生产依赖（无 torch/ML 栈，embedding 自动降级 trigram hash）──
COPY server/requirements-railway.txt .
RUN pip install --no-cache-dir -r requirements-railway.txt

COPY server/ .
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

CMD ["/start.sh"]

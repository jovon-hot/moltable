#!/bin/bash
# Moltable API — Railway start script
cd /app
exec python3 -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"

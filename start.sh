#!/bin/sh
set -e

echo "=== Starting Moltable ==="
echo "DATABASE_URL: ${DATABASE_URL:0:30}..."

echo "=== Running database migrations ==="
for f in /app/migrations/*.sql; do
    if [ -f "$f" ]; then
        echo "Applying: $(basename $f)"
        psql "$DATABASE_URL" -f "$f" 2>&1 || echo "Note: $(basename $f) result above"
    fi
done

echo "=== Starting server ==="
exec /app/server
set -e

echo "Running database migrations..."
for f in /app/migrations/*.sql; do
    if [ -f "$f" ]; then
        echo "Applying migration: $f"
        psql "$DATABASE_URL" -f "$f" || true
    fi
done

echo "Starting server..."
exec /app/server

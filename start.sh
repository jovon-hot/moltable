#!/bin/sh
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

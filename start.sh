#!/bin/sh
set -e

echo "=== Starting Moltable ==="

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL not set"
    exit 1
fi

echo "=== DATABASE_URL present ==="

# Run migration with SSL disabled (for Railway)
echo "=== Running migrations ==="

# Convert postgres:// to postgresql:// and add sslmode=disable
DB_URL=$(echo "$DATABASE_URL" | sed 's|^postgres://|postgresql://|')
if ! echo "$DB_URL" | grep -q "sslmode"; then
    if echo "$DB_URL" | grep -q "?"; then
        DB_URL="${DB_URL}&sslmode=disable"
    else
        DB_URL="${DB_URL}?sslmode=disable"
    fi
fi

for f in /app/migrations/*.sql; do
    if [ -f "$f" ]; then
        echo "Applying: $(basename $f)"
        psql "$DB_URL" -f "$f" 2>&1 || echo "Note: $(basename $f) may already exist"
    fi
done

echo "=== Starting server ==="
exec /app/server

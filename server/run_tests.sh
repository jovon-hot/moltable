#!/usr/bin/env bash
# ── Moltable test runner ──────────────────────────────
# Usage: bash run_tests.sh [-x] [pytest-args...]
#   -x  Stop on first failure

set -euo pipefail

cd "$(dirname "$0")"

echo "🧪 Moltable — Running test suite"
echo "══════════════════════════════════"

# If -x flag is provided, stop on first failure
EXTRA=""
if [[ "${1:-}" == "-x" ]]; then
    EXTRA="-x"
    shift
fi

python -m pytest $EXTRA -v --tb=short "$@"
echo ""
echo "✅ Test suite finished"

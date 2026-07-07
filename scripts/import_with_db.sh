#!/usr/bin/env bash
# Full local pipeline including PostgreSQL load + merge (Steps 5–6).
#
# Usage:
#   bash scripts/import_with_db.sh
#   bash scripts/import_with_db.sh --states-only   # skip LEIE convert
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

STATES_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --states-only) STATES_ONLY=1 ;;
    -h|--help)
      echo "Usage: bash scripts/import_with_db.sh [--states-only]"
      exit 0
      ;;
  esac
done

echo "=== Check PostgreSQL ==="
bash "$SCRIPT_DIR/check_postgres.sh"

PIPELINE_ARGS=()
[ "$STATES_ONLY" = "1" ] && PIPELINE_ARGS+=(--states-only)

echo ""
echo "=== pytest (quick sanity) ==="
python3 -m pytest tests/test_merge_guard.py tests/test_sync_columns.py tests/test_partial_load_policy.py -q

echo ""
echo "=== Full pipeline (load + merge) ==="
python3 -m src.pipeline "${PIPELINE_ARGS[@]}"

echo ""
echo "Local DB import + merge PASSED."

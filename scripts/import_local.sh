#!/usr/bin/env bash
# Local import validation — run after adding/updating raw files or converters.
#
# Usage:
#   bash scripts/import_local.sh              # all sources incl. LEIE if present
#   bash scripts/import_local.sh --states-only   # 39 Medicaid states only
#   bash scripts/import_local.sh --quick        # skip pytest
#
# Default uses --skip-db (no PostgreSQL). For full load + merge locally:
#   bash scripts/check_postgres.sh && bash scripts/import_with_db.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

STATES_ONLY=0
SKIP_TESTS=0
for arg in "$@"; do
  case "$arg" in
    --states-only) STATES_ONLY=1 ;;
    --quick) SKIP_TESTS=1 ;;
    -h|--help)
      echo "Usage: bash scripts/import_local.sh [--states-only] [--quick]"
      exit 0
      ;;
  esac
done

PIPELINE_ARGS=(--skip-db)
[ "$STATES_ONLY" = "1" ] && PIPELINE_ARGS+=(--states-only)

echo "=== Medicaid Exclusion List — local import validation ==="
echo "Project: $PROJECT_DIR"
echo ""

if [ "$SKIP_TESTS" = "0" ]; then
  echo ">>> pytest"
  python3 -m pytest tests/ -q
  echo ""
fi

echo ">>> pipeline ${PIPELINE_ARGS[*]}"
python3 -m src.pipeline "${PIPELINE_ARGS[@]}"
echo ""

echo ">>> inventory"
python3 "$SCRIPT_DIR/inventory_data.py" | tail -20
echo ""

LATEST_AUDIT="$(ls -t docs/artifacts/runs/*/name_audit_*.json 2>/dev/null | head -1 || true)"
LATEST_VALIDATION="$(ls -t docs/artifacts/runs/*/validation_report_*.json 2>/dev/null | head -1 || true)"
echo "=== Review (non-blocking) ==="
[ -n "$LATEST_AUDIT" ] && echo "  Name audit:      $LATEST_AUDIT"
[ -n "$LATEST_VALIDATION" ] && echo "  Validation:      $LATEST_VALIDATION"
echo ""
echo "=== Next: deploy to vesta (optional) ==="
echo "  bash scripts/deploy_vesta.sh"
echo ""
echo "Local import validation PASSED."

#!/usr/bin/env bash
# Integrate cleaned CSVs (and optional raw/converter files) from a colleague repo clone.
# Usage:
#   bash scripts/integrate_colleague_repo.sh /path/to/colleague-clone [STATE_CODE ...]
#
# If STATE_CODE is omitted, copies every *_oig.csv found in data/cleaned/.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_REPO="${1:?Usage: integrate_colleague_repo.sh /path/to/colleague-clone [STATE ...]}"
shift || true
REQUESTED_STATES=("$@")

copy_if_exists() {
  local src="$1"
  local dest="$2"
  if [ -f "$src" ]; then
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    echo "  copied $(basename "$dest")"
  fi
}

integrate_state() {
  local code_lower="$1"
  local code_upper
  code_upper="$(echo "$code_lower" | tr '[:lower:]' '[:upper:]')"

  echo "=== Integrating ${code_upper} from ${SRC_REPO} ==="

  copy_if_exists "$SRC_REPO/data/cleaned/${code_lower}_oig.csv" \
    "$PROJECT_DIR/data/cleaned/${code_lower}_oig.csv"
  copy_if_exists "$SRC_REPO/data/processed/${code_lower}_raw.csv" \
    "$PROJECT_DIR/data/processed/${code_lower}_raw.csv"

  for raw in "$SRC_REPO"/data/raw/*; do
    [ -f "$raw" ] || continue
    copy_if_exists "$raw" "$PROJECT_DIR/data/raw/$(basename "$raw")"
  done

  copy_if_exists "$SRC_REPO/src/convert/${code_lower}.py" \
    "$PROJECT_DIR/src/convert/${code_lower}.py"

  echo "  Manual follow-up for ${code_upper}:"
  echo "    - src/convert/run_all.py"
  echo "    - src/load/load_to_postgres.py (STATE_STAGE_MAP)"
  echo "    - sql/01_create_stage_tables.sql"
  echo "    - sql/03_merge_to_main.sql and sql/04_verify_main_sync.sql"
  echo "    - src/validate/check_import.py (STATE_EXPECTATIONS)"
  echo "    - web/exclusions/queries.py (STATE_NAMES)"
}

if [ ${#REQUESTED_STATES[@]} -gt 0 ]; then
  for state in "${REQUESTED_STATES[@]}"; do
    integrate_state "$(echo "$state" | tr '[:upper:]' '[:lower:]')"
  done
else
  shopt -s nullglob
  for cleaned in "$SRC_REPO"/data/cleaned/*_oig.csv; do
    base="$(basename "$cleaned" _oig.csv)"
    integrate_state "$base"
  done
fi

echo ""
echo "Next: update pipeline config for new states, then run:"
echo "  python3 -m pytest tests/ -v"
echo "  python3 -m src.pipeline --skip-db"

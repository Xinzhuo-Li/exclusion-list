#!/usr/bin/env bash
# Merge one colleague repo into the canonical project with cleanliness checks.
#
# Usage:
#   bash scripts/merge_colleague_state.sh <github-url> <STATE_CODE> [STATE_CODE ...]
#
# Example:
#   bash scripts/merge_colleague_state.sh https://github.com/colleague/repo.git TX
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_URL="${1:?Usage: merge_colleague_state.sh <github-url> <STATE> ...}"
shift
STATES=("$@")

if [ ${#STATES[@]} -eq 0 ]; then
  echo "Provide at least one STATE code (e.g. TX FL)."
  exit 1
fi

REPO_NAME="$(basename "$REPO_URL" .git)"
CLONE_DIR="$PROJECT_DIR/../colleague-repos/$REPO_NAME"
mkdir -p "$PROJECT_DIR/../colleague-repos"

if [ ! -d "$CLONE_DIR/.git" ]; then
  echo "=== Cloning $REPO_URL ==="
  git clone "$REPO_URL" "$CLONE_DIR"
else
  echo "=== Pulling $CLONE_DIR ==="
  git -C "$CLONE_DIR" pull --ff-only
fi

for code in "${STATES[@]}"; do
  upper="$(echo "$code" | tr '[:lower:]' '[:upper:]')"
  lower="$(echo "$code" | tr '[:upper:]' '[:lower:]')"

  if [ -f "$PROJECT_DIR/data/cleaned/${lower}_oig.csv" ]; then
    echo "WARNING: ${upper} already exists in this repo — review for duplicate before overwriting."
    read -r -p "Overwrite ${upper} data from colleague repo? [y/N] " ans
    if [ "$ans" != "y" ] && [ "$ans" != "Y" ]; then
      echo "Skipped ${upper}."
      continue
    fi
  fi

  bash "$SCRIPT_DIR/integrate_colleague_repo.sh" "$CLONE_DIR" "$upper"
done

echo ""
echo "=== Local inventory ==="
python3 "$SCRIPT_DIR/inventory_data.py"

echo ""
echo "=== Required manual updates before pipeline ==="
echo "  1. src/convert/{state}.py  (or: python3 scripts/scaffold_state.py XX name Raw.xlsx)"
echo "  2. src/convert/run_all.py + src/config.py (ALL_SOURCE_STATES)"
echo "  3. sql/01_create_stage_tables.sql + src/load/load_to_postgres.py"
echo "  4. sql/03_merge_to_main.sql (source_state IN list)"
echo "  5. src/validate/check_import.py (STATE_EXPECTATIONS)"
echo "  6. web/exclusions/queries.py (STATE_NAMES) + refresh_sources contributor"
echo "  7. docs/guides/FIELD_SEMANTICS.md, STATE_MAPPING.md, DATA_INVENTORY.md, NAME_HANDLING.md"
echo ""
echo "=== Then validate ==="
echo "  bash scripts/import_local.sh --states-only"
echo "  bash scripts/deploy_vesta.sh"

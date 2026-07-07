#!/usr/bin/env bash
# Pull latest commits from colleague reference clones (does NOT copy into data/raw/).
#
# Usage:
#   bash scripts/pull_colleague_raw.sh              # pull all 4 repos
#   bash scripts/pull_colleague_raw.sh --help
#
# Clone root matches merge_colleague_state.sh (sibling to project dir).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CLONE_ROOT="${CLONE_ROOT:-$PROJECT_DIR/../colleague-repos}"

REPOS=(
  "medicaid-medicare-provider-exclusion-search|AustinGH32"
  "Provider-Exclusion-List-Project|le-luo327"
  "exclusion_list_project|AmeeBeez"
  "medicaid-provider-data-cleaning|FredericYan02"
)

usage() {
  cat <<EOF
Usage: bash scripts/pull_colleague_raw.sh

Pull --ff-only on colleague reference clones under:
  CLONE_ROOT=$CLONE_ROOT

Does not modify data/raw/. After pull, copy files manually using filenames from:
  data/raw/README.md

Then validate: bash scripts/import_local.sh

Environment:
  CLONE_ROOT  Override clone directory (default: ../colleague-repos)
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ $# -gt 0 ]; then
  echo "Unknown argument: $1" >&2
  usage >&2
  exit 1
fi

echo "=== Pull colleague reference repos ==="
echo "CLONE_ROOT: $CLONE_ROOT"
echo ""

mkdir -p "$CLONE_ROOT"
cd "$CLONE_ROOT"

for entry in "${REPOS[@]}"; do
  repo="${entry%%|*}"
  contributor="${entry##*|}"
  path="$CLONE_ROOT/$repo"

  echo "--- $repo ($contributor) ---"
  if [ ! -d "$path/.git" ]; then
    echo "  SKIP: not cloned — see sources/README.md for git clone commands"
    echo ""
    continue
  fi

  before="$(git -C "$path" rev-parse --short HEAD)"
  if git -C "$path" pull --ff-only; then
    after="$(git -C "$path" rev-parse --short HEAD)"
    echo "  HEAD: $before -> $after"
    if [ "$before" != "$after" ]; then
      echo "  CHANGED — review upstream raw files; copy to $PROJECT_DIR/data/raw/ if needed"
      git -C "$path" log --oneline "$before..$after" | head -5 | sed 's/^/    /'
    else
      echo "  Already up to date"
    fi
  else
    echo "  ERROR: git pull failed (merge conflict or diverged branch)" >&2
    exit 1
  fi
  echo ""
done

echo "=== Next steps ==="
echo "  1. Compare clone raw paths with data/raw/README.md filenames"
echo "  2. cp selected files into $PROJECT_DIR/data/raw/"
echo "  3. bash scripts/import_local.sh"
echo "  4. Review docs/artifacts/latest/validation_report_*.json"

#!/usr/bin/env bash
# DEPRECATED — use scripts/deploy_vesta.sh for production or scripts/import_with_db.sh locally.
#
# Legacy server bootstrap script. Does not run merge guards or coverage assertions.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "WARNING: deploy.sh is deprecated. Use:"
echo "  bash scripts/deploy_vesta.sh          # production (vesta)"
echo "  bash scripts/import_with_db.sh      # local load + merge"
exit 1

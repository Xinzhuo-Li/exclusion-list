#!/usr/bin/env bash
# Deploy to vesta: rsync, load, merge, verify, refresh_sources.
# Requires deploy/config.sh and DEPLOY_SSH_PASSWORD in .env
#
# Usage:
#   bash scripts/deploy_vesta.sh
#
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/../deploy/sync_and_merge_noninteractive.sh"

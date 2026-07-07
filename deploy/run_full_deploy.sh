#!/usr/bin/env bash
# Full deploy when vesta SSH is available.
# 1) rsync + ETL reload + merge
# 2) Django setup on server
# 3) Print Caddy/systemd next steps
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$SCRIPT_DIR/config.sh" ]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/config.sh"
fi

if [ -n "${DEPLOY_SSH_PASSWORD:-}" ] || grep -q '^DEPLOY_SSH_PASSWORD=' "$PROJECT_DIR/.env" 2>/dev/null; then
  bash "$SCRIPT_DIR/sync_and_merge_noninteractive.sh"
else
  echo "No DEPLOY_SSH_PASSWORD set — using interactive sync (macOS password dialog)."
  bash "$SCRIPT_DIR/sync_and_merge.sh"
fi

echo ""
echo "=== Remote web production setup ==="
echo "SSH to vesta and run:"
echo "  cd ~/${DEPLOY_REMOTE_DIR:-exclusion-list} && bash deploy/deploy_web_production.sh"
echo ""
echo "vesta uses Caddy (see deploy/Caddyfile.example). After gunicorn is running on :8000:"
echo "  sudo systemctl enable --now exclusion-web   # if using systemd"
echo "  sudo systemctl reload caddy                 # if Caddy config updated"

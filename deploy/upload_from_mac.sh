#!/usr/bin/env bash
# Run on Mac: upload project and execute server setup.
set -euo pipefail

SERVER="${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}"
REMOTE_DIR="exclusion-list"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Uploading project to $SERVER:~/$REMOTE_DIR ==="
ssh "$SERVER" "mkdir -p ~/$REMOTE_DIR"
rsync -avz --delete \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '.env' \
    --exclude 'data/raw' \
    "$PROJECT_DIR/" "$SERVER:~/$REMOTE_DIR/"

echo "=== Running server setup ==="
ssh "$SERVER" "chmod +x ~/$REMOTE_DIR/deploy/server_setup.sh && bash ~/$REMOTE_DIR/deploy/server_setup.sh ~/$REMOTE_DIR"

echo "=== Done. Open pgAdmin tunnel in another terminal: ==="
echo "ssh -L 15432:localhost:5432 $SERVER"

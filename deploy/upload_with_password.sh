#!/usr/bin/env bash
set -euo pipefail

SERVER="${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}"
REMOTE_DIR="exclusion-list"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

SSH_PASS=$(osascript -e 'Tell application "System Events" to display dialog "Enter SSH password for ${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}:" default answer "" with hidden answer' -e 'text returned of result')

run_ssh() {
    expect <<EOF
set timeout 600
spawn ssh -o StrictHostKeyChecking=accept-new $SERVER $1
expect {
    "password:" { send "$SSH_PASS\r"; exp_continue }
    eof
}
EOF
}

run_rsync() {
    expect <<EOF
set timeout 600
spawn rsync -avz --delete --exclude .git --exclude __pycache__ --exclude .env --exclude data/raw "$PROJECT_DIR/" $SERVER:~/$REMOTE_DIR/
expect {
    "password:" { send "$SSH_PASS\r"; exp_continue }
    eof
}
EOF
}

echo "=== Uploading project ==="
run_rsync

echo "=== Running setup on existing PostgreSQL (port 5433) ==="
run_ssh "source ~/.bashrc && bash ~/$REMOTE_DIR/deploy/server_setup_existing_pg.sh ~/$REMOTE_DIR"

echo "=== Done ==="
echo "pgAdmin tunnel: ssh -L 15432:localhost:5433 $SERVER"
echo "pgAdmin connect: localhost:15432, db=exclusion_list, user=aiden, password=(see ~/.bashrc PGPASSWORD)"

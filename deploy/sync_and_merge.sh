#!/usr/bin/env bash
# Run on Mac: sync latest code to vesta, reload DB, merge, verify.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$SCRIPT_DIR/config.sh" ]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/config.sh"
fi

SERVER="${DEPLOY_HOST:?Set DEPLOY_HOST in deploy/config.sh, e.g. export DEPLOY_HOST=aiden@107.181.241.82}"
REMOTE_DIR="${DEPLOY_REMOTE_DIR:-exclusion-list}"

SSH_PASS=$(osascript -e 'Tell application "System Events" to display dialog "Enter SSH password for vesta:" default answer "" with hidden answer' -e 'text returned of result')

run_rsync() {
  expect <<EOF
set timeout 300
spawn rsync -avz --exclude .git --exclude __pycache__ --exclude .env --exclude .venv "$PROJECT_DIR/" $SERVER:~/$REMOTE_DIR/
expect "password:" { send "$SSH_PASS\r" }
expect eof
EOF
}

run_remote() {
  expect <<EOF
set timeout 600
spawn ssh -o StrictHostKeyChecking=accept-new $SERVER "cd ~/$REMOTE_DIR && set -a && test -f .env && . ./.env && set +a && source .venv/bin/activate && psql -h localhost -p 5433 -U aiden -d exclusion_list -f sql/06_alter_add_list_source.sql && python3 -m src.load.load_to_postgres && psql -h localhost -p 5433 -U aiden -d exclusion_list -f sql/03_merge_to_main.sql && psql -h localhost -p 5433 -U aiden -d exclusion_list -f sql/04_verify_main_sync.sql"
expect "password:" { send "$SSH_PASS\r" }
expect eof
EOF
}

echo "=== Uploading latest code to vesta ==="
run_rsync

echo "=== Reload, merge, verify on vesta ==="
run_remote

echo "=== Refresh Django data source metadata (optional) ==="
expect <<EOF
set timeout 120
spawn ssh -o StrictHostKeyChecking=accept-new $SERVER "source ~/.bashrc && cd ~/$REMOTE_DIR && source .venv/bin/activate && cd web && python manage.py migrate --noinput && python manage.py refresh_sources || true"
expect "password:" { send "$SSH_PASS\r" }
expect eof
EOF

echo "=== Done ==="

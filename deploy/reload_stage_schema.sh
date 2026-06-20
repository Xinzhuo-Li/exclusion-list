#!/usr/bin/env bash
# Recreate stage tables (NOT NULL schema) and reload data on vesta.
set -euo pipefail

SERVER="${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}"
REMOTE_DIR="exclusion-list"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

SSH_PASS=$(osascript -e 'Tell application "System Events" to display dialog "Enter SSH password for ${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}:" default answer "" with hidden answer' -e 'text returned of result')

expect <<EOF
set timeout 300
spawn rsync -avz "$PROJECT_DIR/sql/01_create_stage_tables.sql" $SERVER:~/$REMOTE_DIR/sql/
expect "password:" { send "$SSH_PASS\r" }
expect eof
EOF

expect <<EOF
set timeout 300
spawn rsync -avz "$PROJECT_DIR/src/load/load_to_postgres.py" $SERVER:~/$REMOTE_DIR/src/load/
expect "password:" { send "$SSH_PASS\r" }
expect eof
EOF

expect <<EOF
set timeout 600
spawn ssh -o StrictHostKeyChecking=accept-new $SERVER "source ~/.bashrc && cd ~/$REMOTE_DIR && source .venv/bin/activate && python3 -m src.load.load_to_postgres && PGPASSWORD=\$PGPASSWORD psql -h localhost -p 5433 -U aiden -d exclusion_list -f sql/03_merge_to_main.sql"
expect "password:" { send "$SSH_PASS\r" }
expect eof
EOF

echo "Stage tables recreated with NOT NULL columns and data reloaded."

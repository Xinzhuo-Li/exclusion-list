#!/usr/bin/env bash
set -euo pipefail
SERVER="${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}"
REMOTE_DIR="exclusion-list"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SSH_PASS=$(osascript -e 'Tell application "System Events" to display dialog "Enter SSH password for ${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}:" default answer "" with hidden answer' -e 'text returned of result')

expect <<EOF
set timeout 120
spawn rsync -avz "$PROJECT_DIR/deploy/check_stage_nulls.sh" $SERVER:~/$REMOTE_DIR/deploy/
expect "password:" { send "$SSH_PASS\r" }
expect eof
EOF

expect <<EOF
set timeout 120
spawn ssh -o StrictHostKeyChecking=accept-new $SERVER "source ~/.bashrc && PGPASSWORD=\\\$PGPASSWORD psql -h localhost -p 5433 -U aiden -d exclusion_list -f ~/exclusion-list/sql/03_merge_to_main.sql && bash ~/exclusion-list/deploy/check_stage_nulls.sh"
expect "password:" { send "$SSH_PASS\r" }
expect eof
EOF

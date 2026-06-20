#!/usr/bin/env bash
set -euo pipefail

SERVER="${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}"
REMOTE="bash -s"

SSH_PASS=$(osascript -e 'Tell application "System Events" to display dialog "Enter SSH password for ${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}:" default answer "" with hidden answer' -e 'text returned of result')

expect <<EOF
set timeout 60
spawn ssh -o StrictHostKeyChecking=accept-new $SERVER $REMOTE
expect "password:" { send "$SSH_PASS\r" }
expect "$ "
send "ls -la ~/.pgpass 2>/dev/null || echo no_pgpass\r"
expect "$ "
send "env | grep -i PG || echo no_pg_env\r"
expect "$ "
send "psql -h localhost -p 5433 -U aiden -d postgres -c 'SELECT 1' 2>&1 | head -3\r"
expect "$ "
send "exit\r"
expect eof
EOF

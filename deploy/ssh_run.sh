#!/usr/bin/env bash
set -euo pipefail

SERVER="${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}"
CMD="${1:-hostname}"

SSH_PASS=$(osascript -e 'Tell application "System Events" to display dialog "Enter SSH password for ${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}:" default answer "" with hidden answer' -e 'text returned of result')

expect <<EOF
set timeout 120
spawn ssh -o StrictHostKeyChecking=accept-new $SERVER "$CMD"
expect {
    "password:" { send "$SSH_PASS\r"; exp_continue }
    eof
}
EOF

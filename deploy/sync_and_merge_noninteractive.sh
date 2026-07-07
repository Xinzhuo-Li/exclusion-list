#!/usr/bin/env bash
# Non-interactive sync: rsync code to vesta, reload DB, merge, verify, Django migrate.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$SCRIPT_DIR/config.sh" ]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/config.sh"
fi

SERVER="${DEPLOY_HOST:?Set DEPLOY_HOST in deploy/config.sh}"
REMOTE_DIR="${DEPLOY_REMOTE_DIR:-exclusion-list}"
PGPORT="${PGPORT:-5433}"

if [ -z "${DEPLOY_SSH_PASSWORD:-}" ] && [ -f "$PROJECT_DIR/.env" ]; then
  DEPLOY_SSH_PASSWORD="$(grep -E '^DEPLOY_SSH_PASSWORD=' "$PROJECT_DIR/.env" | cut -d= -f2- || true)"
fi
if [ -z "${DEPLOY_SSH_PASSWORD:-}" ]; then
  echo "Set DEPLOY_SSH_PASSWORD in the environment or add DEPLOY_SSH_PASSWORD=... to .env"
  exit 1
fi

export DEPLOY_SSH_PASSWORD
export DEPLOY_HOST="${SERVER}"

ssh_with_pass() {
  export REMOTE_CMD="$1"
  expect <<'EOF'
set timeout 900
spawn ssh -o StrictHostKeyChecking=accept-new $env(DEPLOY_HOST) $env(REMOTE_CMD)
expect {
  -re "(?i)password:" {
    send -- "$env(DEPLOY_SSH_PASSWORD)\r"
    exp_continue
  }
  eof
}
EOF
}

echo "=== Uploading project to ${SERVER}:~/${REMOTE_DIR} ==="
export RSYNC_SOURCE="${PROJECT_DIR}/"
export RSYNC_DEST="${SERVER}:~/${REMOTE_DIR}/"
expect <<'EOF'
set timeout 600
spawn rsync -avz --exclude .git --exclude __pycache__ --exclude .env --exclude .venv --exclude web/staticfiles $env(RSYNC_SOURCE) $env(RSYNC_DEST)
expect {
  -re "(?i)password:" {
    send -- "$env(DEPLOY_SSH_PASSWORD)\r"
    exp_continue
  }
  eof
}
EOF

echo "=== Reload, merge, verify on vesta ==="
MERGE_CMD="cd ~/${REMOTE_DIR} && set -a && test -f .env && . ./.env && set +a && source .venv/bin/activate && pip install -q -r requirements.txt && psql -h localhost -p ${PGPORT} -U aiden -d exclusion_list -f sql/01_create_stage_tables.sql && psql -h localhost -p ${PGPORT} -U aiden -d exclusion_list -f sql/06_alter_add_list_source.sql && python3 -m src.load.load_to_postgres && python3 -c \"from src.load.load_to_postgres import get_connection; from src.load.merge_guard import validate_staging_before_merge; validate_staging_before_merge(get_connection())\" && psql -h localhost -p ${PGPORT} -U aiden -d exclusion_list -f sql/03_merge_to_main.sql && psql -h localhost -p ${PGPORT} -U aiden -d exclusion_list -f sql/04_verify_main_sync.sql && psql -h localhost -p ${PGPORT} -U aiden -d exclusion_list -v ON_ERROR_STOP=1 -f sql/05_assert_coverage.sql"
ssh_with_pass "${MERGE_CMD}"

echo "=== Django setup + migrate ==="
DJANGO_CMD="source ~/.bashrc && cd ~/${REMOTE_DIR} && bash deploy/django_setup.sh && cd web && source ../.venv/bin/activate && python manage.py migrate --noinput && python manage.py refresh_sources || true"
ssh_with_pass "${DJANGO_CMD}"

echo "=== Done ==="

#!/usr/bin/env bash
# One-time production web setup on vesta (run on server after sync).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REMOTE_DIR="${DEPLOY_REMOTE_DIR:-exclusion-list}"

cd "$PROJECT_ROOT"
bash "$SCRIPT_DIR/django_setup.sh"

ENV_FILE="$PROJECT_ROOT/.env"
if [ ! -f "$ENV_FILE" ]; then
  cat > "$ENV_FILE" <<ENV
PGHOST=localhost
PGPORT=5433
PGDATABASE=exclusion_list
PGUSER=aiden
PGPASSWORD=CHANGE_ME
DJANGO_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')
DJANGO_DEBUG=False
ALLOWED_HOSTS=107.181.241.82,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://107.181.241.82
ENV
  echo "Created $ENV_FILE — edit PGPASSWORD before starting the service."
fi

echo "Optional (requires sudo): install systemd + Caddy/nginx"
echo "  sudo cp deploy/exclusion-web.service.example /etc/systemd/system/exclusion-web.service"
echo "  # Edit paths if REMOTE_DIR differs from ~/exclusion-list"
echo "  sudo systemctl daemon-reload && sudo systemctl enable --now exclusion-web"
echo ""
echo "  # vesta uses Caddy — see deploy/Caddyfile.example"
echo "  sudo systemctl reload caddy"
echo ""
echo "  # Or nginx: deploy/nginx.conf.example"
echo ""
echo "Quick test without nginx:"
echo "  cd web && ../.venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000"

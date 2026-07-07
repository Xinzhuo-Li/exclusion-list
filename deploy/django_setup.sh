#!/usr/bin/env bash
# Deploy Django web app on vesta (run on server after ETL is configured).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WEB_DIR="$PROJECT_ROOT/web"
VENV_DIR="${VENV_DIR:-$PROJECT_ROOT/.venv}"

echo "=== Django web setup ==="
cd "$PROJECT_ROOT"

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt

cd "$WEB_DIR"
python manage.py migrate --noinput
python manage.py collectstatic --noinput

if python manage.py shell -c "from exclusions.models import ExclusionRecord; print(ExclusionRecord.objects.count())" 2>/dev/null; then
  python manage.py refresh_sources || true
fi

echo ""
echo "Setup complete. Start the server with:"
echo "  cd web && gunicorn config.wsgi:application --bind 0.0.0.0:8000"
echo ""
echo "Or install the systemd service:"
echo "  sudo cp deploy/exclusion-web.service.example /etc/systemd/system/exclusion-web.service"
echo "  sudo systemctl enable --now exclusion-web"

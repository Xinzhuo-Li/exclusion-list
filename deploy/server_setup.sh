#!/usr/bin/env bash
# Full server setup: PostgreSQL, Python deps, load data, verify, merge.
set -euo pipefail

PROJECT_DIR="${1:-$HOME/exclusion-list}"
DB_PASSWORD="${DB_PASSWORD:-ExclList2026!Vesta}"
SUDO_PASSWORD="${SUDO_PASSWORD:-}"

sudo_cmd() {
    if [ -n "$SUDO_PASSWORD" ]; then
        echo "$SUDO_PASSWORD" | sudo -S "$@"
    elif sudo -n true 2>/dev/null; then
        sudo "$@"
    else
        echo "ERROR: sudo password required. Set SUDO_PASSWORD env var." >&2
        exit 1
    fi
}

echo "=== Project dir: $PROJECT_DIR ==="
cd "$PROJECT_DIR"

echo "=== Ensuring PostgreSQL is installed and running ==="
if ! command -v psql &>/dev/null; then
    sudo_cmd apt update
    sudo_cmd apt install -y postgresql postgresql-contrib
fi
sudo_cmd systemctl enable postgresql
sudo_cmd systemctl start postgresql

echo "=== Creating database user and database ==="
sudo_cmd -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'aiden') THEN
        CREATE USER aiden WITH PASSWORD '${DB_PASSWORD}';
    ELSE
        ALTER USER aiden WITH PASSWORD '${DB_PASSWORD}';
    END IF;
END
\$\$;
SELECT 'CREATE DATABASE exclusion_list OWNER aiden'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'exclusion_list')\gexec
GRANT ALL PRIVILEGES ON DATABASE exclusion_list TO aiden;
SQL

sudo_cmd -u postgres psql -d exclusion_list -v ON_ERROR_STOP=1 <<SQL
GRANT ALL ON SCHEMA public TO aiden;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO aiden;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO aiden;
SQL

echo "=== Writing .env ==="
cat > .env <<ENV
PGHOST=localhost
PGPORT=5432
PGDATABASE=exclusion_list
PGUSER=aiden
PGPASSWORD=${DB_PASSWORD}
ENV

echo "=== Installing Python dependencies ==="
pip3 install --user -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt

echo "=== Loading data into PostgreSQL ==="
python3 -m src.load.load_to_postgres

echo "=== Verifying row counts ==="
export PGPASSWORD="${DB_PASSWORD}"
psql -h localhost -U aiden -d exclusion_list <<'SQL'
SELECT 'stage_maryland' AS tbl, COUNT(*) FROM stage_maryland
UNION ALL SELECT 'stage_massachusetts', COUNT(*) FROM stage_massachusetts
UNION ALL SELECT 'stage_michigan', COUNT(*) FROM stage_michigan
UNION ALL SELECT 'stage_mississippi', COUNT(*) FROM stage_mississippi
UNION ALL SELECT 'stage_montana', COUNT(*) FROM stage_montana
UNION ALL SELECT 'stage_nebraska', COUNT(*) FROM stage_nebraska
UNION ALL SELECT 'cleaned_staging', COUNT(*) FROM cleaned_staging;

SELECT source_state, COUNT(*) FROM cleaned_staging
GROUP BY source_state ORDER BY source_state;
SQL

echo "=== Merging into exclusion_main ==="
psql -h localhost -U aiden -d exclusion_list -f sql/03_merge_to_main.sql

echo "=== Post-merge verification ==="
psql -h localhost -U aiden -d exclusion_list <<'SQL'
SELECT source_state, COUNT(*) FROM exclusion_main
GROUP BY source_state ORDER BY source_state;
SELECT COUNT(*) AS total FROM exclusion_main;
SQL

echo "=== Deployment complete ==="
echo "DB password: ${DB_PASSWORD}"
echo "pgAdmin: ssh -L 15432:localhost:5432 ${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}"
echo "         Connect to localhost:15432, db=exclusion_list, user=aiden"

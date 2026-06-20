#!/usr/bin/env bash
# Setup user-space PostgreSQL (no sudo required), load data, verify, merge.
set -euo pipefail

PROJECT_DIR="${1:-$HOME/exclusion-list}"
PGDATA="${PGDATA:-$HOME/pgdata-exclusion}"
PGPORT="${PGPORT:-5434}"
DB_PASSWORD="${DB_PASSWORD:-ExclList2026!Vesta}"
PGLOG="$HOME/pgdata-exclusion.log"

echo "=== Project dir: $PROJECT_DIR ==="
cd "$PROJECT_DIR"

echo "=== Initializing user-space PostgreSQL on port $PGPORT ==="
if [ ! -d "$PGDATA" ]; then
    initdb -D "$PGDATA" --auth-local=trust --auth-host=scram-sha-256
fi

if ! pg_ctl -D "$PGDATA" status >/dev/null 2>&1; then
    pg_ctl -D "$PGDATA" -l "$PGLOG" -o "-p $PGPORT" start
    sleep 2
fi

echo "=== Creating database ==="
psql -h localhost -p "$PGPORT" -d postgres -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'aiden') THEN
        CREATE USER aiden WITH PASSWORD '${DB_PASSWORD}' SUPERUSER;
    ELSE
        ALTER USER aiden WITH PASSWORD '${DB_PASSWORD}';
    END IF;
END
\$\$;
SELECT 'CREATE DATABASE exclusion_list OWNER aiden'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'exclusion_list')\gexec
SQL

echo "=== Writing .env ==="
cat > .env <<ENV
PGHOST=localhost
PGPORT=${PGPORT}
PGDATABASE=exclusion_list
PGUSER=aiden
PGPASSWORD=${DB_PASSWORD}
ENV

echo "=== Installing Python dependencies ==="
pip3 install --user psycopg2-binary python-dotenv 2>/dev/null || pip3 install psycopg2-binary python-dotenv

echo "=== Loading data into PostgreSQL ==="
python3 -m src.load.load_to_postgres

echo "=== Verifying row counts ==="
export PGPASSWORD="${DB_PASSWORD}"
psql -h localhost -p "$PGPORT" -U aiden -d exclusion_list <<'SQL'
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
psql -h localhost -p "$PGPORT" -U aiden -d exclusion_list -f sql/03_merge_to_main.sql

echo "=== Post-merge verification ==="
psql -h localhost -p "$PGPORT" -U aiden -d exclusion_list <<'SQL'
SELECT source_state, COUNT(*) FROM exclusion_main
GROUP BY source_state ORDER BY source_state;
SELECT COUNT(*) AS total FROM exclusion_main;
SQL

echo "=== Deployment complete ==="
echo "PostgreSQL: localhost:$PGPORT (user-space, data in $PGDATA)"
echo "DB password: ${DB_PASSWORD}"
echo "pgAdmin tunnel: ssh -L 15432:localhost:$PGPORT ${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}"

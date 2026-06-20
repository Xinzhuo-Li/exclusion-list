#!/usr/bin/env bash
# Setup using existing system PostgreSQL on port 5433 (no sudo required).
set -euo pipefail

PROJECT_DIR="${1:-$HOME/exclusion-list}"
DB_PASSWORD="${DB_PASSWORD:?Set DB_PASSWORD or source ~/.bashrc on server}"
PGPORT="${PGPORT:-5433}"
PGHOST="${PGHOST:-localhost}"
PGUSER="${PGUSER:-aiden}"
PGADMIN_USER="${PGADMIN_USER:-verbus}"

export PGPORT PGHOST PGPASSWORD="$DB_PASSWORD"

echo "=== Project dir: $PROJECT_DIR ==="
cd "$PROJECT_DIR"

echo "=== Ensuring database exclusion_list exists ==="
if ! psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -w -tc "SELECT 1 FROM pg_database WHERE datname='exclusion_list'" | grep -q 1; then
    echo "Creating exclusion_list database as $PGADMIN_USER..."
    PGPASSWORD="$DB_PASSWORD" createdb -h "$PGHOST" -p "$PGPORT" -U "$PGADMIN_USER" exclusion_list
    psql -h "$PGHOST" -p "$PGPORT" -U "$PGADMIN_USER" -d postgres -w -c "GRANT ALL PRIVILEGES ON DATABASE exclusion_list TO ${PGUSER};"
fi
psql -h "$PGHOST" -p "$PGPORT" -U "$PGADMIN_USER" -d exclusion_list -w -c "GRANT ALL ON SCHEMA public TO ${PGUSER}; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${PGUSER}; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${PGUSER};"

echo "=== Writing .env ==="
cat > .env <<ENV
PGHOST=${PGHOST}
PGPORT=${PGPORT}
PGDATABASE=exclusion_list
PGUSER=${PGUSER}
PGPASSWORD=${DB_PASSWORD}
ENV

echo "=== Setting up Python virtual environment ==="
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q psycopg2-binary python-dotenv

echo "=== Loading data into PostgreSQL ==="
python3 -m src.load.load_to_postgres

echo "=== Verifying row counts ==="
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d exclusion_list <<'SQL'
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
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d exclusion_list -f sql/03_merge_to_main.sql

echo "=== Post-merge verification ==="
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d exclusion_list <<'SQL'
SELECT source_state, COUNT(*) FROM exclusion_main
GROUP BY source_state ORDER BY source_state;
SELECT COUNT(*) AS total FROM exclusion_main;
SQL

echo "=== Deployment complete ==="
echo "PostgreSQL: ${PGHOST}:${PGPORT}, db=exclusion_list, user=${PGUSER}"
echo "pgAdmin tunnel: ssh -L 15432:localhost:${PGPORT} ${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}"

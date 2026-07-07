#!/usr/bin/env bash
# Check PostgreSQL connectivity using .env credentials.
#
# Usage:
#   bash scripts/check_postgres.sh
#   bash scripts/check_postgres.sh --quiet   # exit code only
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
QUIET=0

for arg in "$@"; do
  case "$arg" in
    -q|--quiet) QUIET=1 ;;
    -h|--help)
      echo "Usage: bash scripts/check_postgres.sh [--quiet]"
      exit 0
      ;;
  esac
done

if [ ! -f "$PROJECT_DIR/.env" ]; then
  [ "$QUIET" = "0" ] && echo "ERROR: .env not found. Copy .env.example and configure PGHOST/PGPORT." >&2
  exit 1
fi

set -a
# shellcheck source=/dev/null
source "$PROJECT_DIR/.env"
set +a

python3 <<PY
import os
import sys

quiet = ${QUIET}

try:
    import psycopg2
except ImportError:
    if not quiet:
        print("ERROR: psycopg2 not installed. pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

host = os.environ.get("PGHOST", "localhost")
port = os.environ.get("PGPORT", "5432")
dbname = os.environ.get("PGDATABASE", "exclusion_list")
user = os.environ.get("PGUSER", "postgres")
password = os.environ.get("PGPASSWORD", "")

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        connect_timeout=5,
    )
    cur = conn.cursor()
    cur.execute("SELECT 1")
    cur.fetchone()
    conn.close()
except Exception as exc:
    if not quiet:
        print(
            f"ERROR: Cannot connect to PostgreSQL at {host}:{port}/{dbname} as {user}\\n"
            f"  {exc}\\n"
            "  For local merge testing: start PG or configure SSH tunnel in deploy/config.sh.\\n"
            "  For production merge: bash deploy/sync_and_merge_noninteractive.sh",
            file=sys.stderr,
        )
    sys.exit(1)

if not quiet:
    print(f"PostgreSQL OK: {host}:{port}/{dbname} (user={user})")
PY

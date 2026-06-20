#!/usr/bin/env bash
# Deploy and run exclusion list pipeline on Linux server.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Installing Python dependencies ==="
pip3 install -r requirements.txt

echo "=== Running convert and clean (Steps 1-2) ==="
python3 -m src.convert.run_all

echo "=== Running validation (Step 4) ==="
python3 -m src.validate.check_import

if [ ! -f .env ]; then
    echo "WARNING: .env not found. Copy .env.example and configure PostgreSQL credentials."
    echo "Skipping database load. Run 'python3 -m src.pipeline' after configuring .env"
    exit 0
fi

echo "=== Loading into PostgreSQL (Step 3) ==="
python3 -m src.load.load_to_postgres

echo "=== Merging into exclusion_main (Step 5) ==="
python3 - <<'PY'
from src.load.load_to_postgres import ROOT_DIR, get_connection

sql_path = ROOT_DIR / "sql" / "03_merge_to_main.sql"
with get_connection() as conn, sql_path.open(encoding="utf-8") as handle:
    with conn.cursor() as cur:
        cur.execute(handle.read())
    conn.commit()
print("Merge complete.")
PY

echo "=== Deployment complete ==="

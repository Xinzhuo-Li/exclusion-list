#!/usr/bin/env bash
set -euo pipefail
set -a
[ -f ~/exclusion-list/.env ] && . ~/exclusion-list/.env
set +a

echo "=== Databases with exclusion_main table ==="
psql -h localhost -p 5433 -U aiden -d postgres -w -t -A -c \
  "SELECT datname FROM pg_database WHERE datistemplate = false AND datname <> 'postgres' ORDER BY datname;" |
while IFS= read -r db; do
  [ -z "$db" ] && continue
  has=$(psql -h localhost -p 5433 -U aiden -d "$db" -w -t -A -c \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='exclusion_main';" 2>/dev/null || echo 0)
  if [ "$has" = "1" ]; then
    rows=$(psql -h localhost -p 5433 -U aiden -d "$db" -w -t -A -c "SELECT COUNT(*) FROM exclusion_main;" 2>/dev/null || echo "?")
    echo "$db | exclusion_main rows: $rows"
    psql -h localhost -p 5433 -U aiden -d "$db" -w -c \
      "SELECT source_state, COUNT(*) FROM exclusion_main GROUP BY source_state ORDER BY 1;" 2>/dev/null || true
    echo "---"
  fi
done

echo ""
echo "=== Databases with cleaned_staging table ==="
psql -h localhost -p 5433 -U aiden -d postgres -w -t -A -c \
  "SELECT datname FROM pg_database WHERE datistemplate = false AND datname <> 'postgres' ORDER BY datname;" |
while IFS= read -r db; do
  [ -z "$db" ] && continue
  has=$(psql -h localhost -p 5433 -U aiden -d "$db" -w -t -A -c \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='cleaned_staging';" 2>/dev/null || echo 0)
  if [ "$has" = "1" ]; then
    echo "$db"
  fi
done

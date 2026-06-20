#!/usr/bin/env bash
set -euo pipefail

source ~/.bashrc 2>/dev/null || true
export PGPASSWORD="${PGPASSWORD:?Set PGPASSWORD before running}"
PGPORT="${PGPORT:-5433}"

psql -h localhost -p "$PGPORT" -U aiden -d exclusion_list <<'SQL'
\echo '=== NULL count in stage_maryland (should be 0) ==='
SELECT COUNT(*) AS null_cells FROM (
  SELECT last_name_org, first_name, entity_type, sanction_type, npi,
         license_no, termination_date, address, city_state_zip
  FROM stage_maryland
) t,
LATERAL (VALUES
  (t.last_name_org), (t.first_name), (t.entity_type), (t.sanction_type),
  (t.npi), (t.license_no), (t.termination_date), (t.address), (t.city_state_zip)
) v(val)
WHERE v.val IS NULL;

\echo '=== id column sample ==='
SELECT id, last_name_org, npi FROM stage_maryland ORDER BY id LIMIT 5;

\echo '=== row counts ==='
SELECT 'stage_maryland' AS tbl, COUNT(*) FROM stage_maryland
UNION ALL SELECT 'exclusion_main', COUNT(*) FROM exclusion_main;
SQL

#!/usr/bin/env bash
# Audit vesta PostgreSQL and project dirs for 39-state + LEIE production baseline.
set -euo pipefail

# Active Medicaid states (must match src/config.py ALL_SOURCE_STATES).
ACTIVE_STATES="MD MA MI MS MT NE CA NY NC ND OH NJ PA GA HI ID IL IN IA KS KY LA ME AL AK AZ AR CO CT DE DC FL SC TN TX VT WA WV WY"
ACTIVE_STATES_SQL="'MD','MA','MI','MS','MT','NE','CA','NY','NC','ND','OH','NJ','PA','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','AL','AK','AZ','AR','CO','CT','DE','DC','FL','SC','TN','TX','VT','WA','WV','WY'"
EXPECTED_STATE_ROWS=173312
EXPECTED_FEDERAL_ROWS=83464
EXPECTED_TOTAL_ROWS=256776
EXPECTED_STATE_SOURCES=39

echo "========== HOST =========="
hostname
date -u

echo ""
echo "========== PROJECT DIRS (aiden home) =========="
ls -la ~ | grep -iE 'exclusion|medicaid|pgdata' || true
for d in ~/exclusion-list ~/medicaid-exclusion-list ~/exclusion_list; do
  if [ -d "$d" ]; then
    echo "--- $d ---"
    du -sh "$d" 2>/dev/null || true
    ls "$d" 2>/dev/null | head -20
  fi
done

echo ""
echo "========== POSTGRES PROCESSES / PORTS =========="
pgrep -af postgres || true
ss -tlnp 2>/dev/null | grep -E ':543[0-9]' || netstat -tlnp 2>/dev/null | grep -E ':543[0-9]' || true

echo ""
echo "========== DATABASES (port 5433) =========="
set -a
[ -f ~/exclusion-list/.env ] && . ~/exclusion-list/.env
set +a
export PGPASSWORD="${PGPASSWORD:-}"

psql -h localhost -p 5433 -U aiden -d postgres -w -c \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba) AS owner, pg_size_pretty(pg_database_size(datname)) AS size
   FROM pg_database WHERE datistemplate = false ORDER BY datname;" 2>&1 || echo "psql 5433 failed"

echo ""
echo "========== exclusion_list TABLES =========="
psql -h localhost -p 5433 -U aiden -d exclusion_list -w -c "\dt" 2>&1 || true

echo ""
echo "========== ROW COUNTS (main vs staging) =========="
psql -h localhost -p 5433 -U aiden -d exclusion_list -w -c \
  "SELECT 'exclusion_main' AS tbl, COUNT(*) FROM exclusion_main
   UNION ALL SELECT 'cleaned_staging', COUNT(*) FROM cleaned_staging;" 2>&1 || true

echo ""
echo "========== BY list_source (expected state=${EXPECTED_STATE_ROWS}, federal=${EXPECTED_FEDERAL_ROWS}) =========="
psql -h localhost -p 5433 -U aiden -d exclusion_list -w -c \
  "SELECT list_source, COUNT(*) AS cnt,
          CASE list_source
            WHEN 'state' THEN ${EXPECTED_STATE_ROWS}
            WHEN 'federal' THEN ${EXPECTED_FEDERAL_ROWS}
          END AS expected,
          COUNT(*) - CASE list_source
            WHEN 'state' THEN ${EXPECTED_STATE_ROWS}
            WHEN 'federal' THEN ${EXPECTED_FEDERAL_ROWS}
            ELSE 0
          END AS delta
   FROM exclusion_main
   GROUP BY list_source
   ORDER BY 1;" 2>&1 || true

echo ""
echo "========== TOTAL ROWS (expected ${EXPECTED_TOTAL_ROWS}) =========="
psql -h localhost -p 5433 -U aiden -d exclusion_list -w -c \
  "SELECT COUNT(*) AS total,
          ${EXPECTED_TOTAL_ROWS} AS expected,
          COUNT(*) - ${EXPECTED_TOTAL_ROWS} AS delta
   FROM exclusion_main;" 2>&1 || true

echo ""
echo "========== BY source_state (main vs staging delta) =========="
psql -h localhost -p 5433 -U aiden -d exclusion_list -w -c \
  "SELECT COALESCE(m.source_state, s.source_state) AS state,
          COALESCE(m.cnt, 0) AS main_cnt,
          COALESCE(s.cnt, 0) AS staging_cnt,
          COALESCE(m.cnt, 0) - COALESCE(s.cnt, 0) AS delta
   FROM (SELECT source_state, COUNT(*) cnt FROM exclusion_main GROUP BY source_state) m
   FULL OUTER JOIN (SELECT source_state, COUNT(*) cnt FROM cleaned_staging GROUP BY source_state) s
   USING (source_state)
   ORDER BY state;" 2>&1 || true

echo ""
echo "========== Active 39-state coverage check =========="
MISSING_STATES_SQL="SELECT x.st AS missing_state FROM (VALUES $(echo "$ACTIVE_STATES" | awk '{for(i=1;i<=NF;i++) printf "(%s)%s", $i, (i<NF?",":"")}') ) AS x(st) WHERE x.st NOT IN (SELECT DISTINCT source_state FROM exclusion_main WHERE list_source = 'state') ORDER BY 1;"
psql -h localhost -p 5433 -U aiden -d exclusion_list -w -c "$MISSING_STATES_SQL" 2>&1 || true

psql -h localhost -p 5433 -U aiden -d exclusion_list -w -c \
  "SELECT COUNT(DISTINCT source_state) AS state_sources,
          ${EXPECTED_STATE_SOURCES} AS expected
   FROM exclusion_main WHERE list_source = 'state';" 2>&1 || true

echo ""
echo "========== States in main outside active 39-state set =========="
psql -h localhost -p 5433 -U aiden -d exclusion_list -w -c \
  "SELECT source_state, COUNT(*) FROM exclusion_main
   WHERE list_source = 'state'
     AND source_state NOT IN (${ACTIVE_STATES_SQL})
   GROUP BY source_state ORDER BY 1;" 2>&1 || true

echo ""
echo "========== EXACT DUPLICATES in exclusion_main (all business cols) =========="
psql -h localhost -p 5433 -U aiden -d exclusion_list -w -c \
  "SELECT COUNT(*) AS duplicate_row_groups FROM (
     SELECT lastname, firstname, midname, busname, general, specialty,
            upin, npi, dob, address, city, state, zip_code,
            excltype, excldate, reindate, waiverdate, waiverstate, list_source, source_state,
            COUNT(*) AS n
     FROM exclusion_main
     GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
     HAVING COUNT(*) > 1
   ) t;" 2>&1 || true

echo ""
echo "========== OTHER PG DATA DIRS =========="
ls -la ~/pgdata* 2>/dev/null || echo "no ~/pgdata*"
ls -la ~/.pgdata* 2>/dev/null || true

echo ""
echo "========== DONE =========="

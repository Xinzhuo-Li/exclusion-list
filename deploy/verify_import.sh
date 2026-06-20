#!/usr/bin/env bash
set -euo pipefail

source ~/.bashrc 2>/dev/null || true
export PGPASSWORD="${PGPASSWORD:?Set PGPASSWORD before running}"
PGPORT="${PGPORT:-5433}"

psql -h localhost -p "$PGPORT" -U aiden -d exclusion_list -v ON_ERROR_STOP=1 <<'SQL'
\echo '=== TABLE ROW COUNTS ==='
SELECT 'stage_maryland' AS tbl, COUNT(*) FROM stage_maryland
UNION ALL SELECT 'stage_massachusetts', COUNT(*) FROM stage_massachusetts
UNION ALL SELECT 'stage_michigan', COUNT(*) FROM stage_michigan
UNION ALL SELECT 'stage_mississippi', COUNT(*) FROM stage_mississippi
UNION ALL SELECT 'stage_montana', COUNT(*) FROM stage_montana
UNION ALL SELECT 'stage_nebraska', COUNT(*) FROM stage_nebraska
UNION ALL SELECT 'cleaned_staging', COUNT(*) FROM cleaned_staging
UNION ALL SELECT 'exclusion_main', COUNT(*) FROM exclusion_main;

\echo '=== CLEANED_STAGING BY STATE ==='
SELECT source_state, COUNT(*) FROM cleaned_staging GROUP BY source_state ORDER BY 1;

\echo '=== EXCLUSION_MAIN BY STATE ==='
SELECT source_state, COUNT(*) FROM exclusion_main GROUP BY source_state ORDER BY 1;

\echo '=== QUALITY: empty source_state ==='
SELECT COUNT(*) AS empty_source_state FROM exclusion_main WHERE source_state IS NULL OR source_state = '';

\echo '=== QUALITY: invalid NPI format ==='
SELECT COUNT(*) AS invalid_npi FROM exclusion_main WHERE npi <> '' AND npi !~ '^\d{10}$';

\echo '=== QUALITY: invalid EXCLDATE format ==='
SELECT COUNT(*) AS invalid_excldate FROM exclusion_main WHERE excldate <> '' AND excldate !~ '^\d{8}$';

\echo '=== QUALITY: MS bad REINDATE 29991231 ==='
SELECT COUNT(*) AS ms_bad_reindate FROM exclusion_main WHERE source_state = 'MS' AND reindate = '29991231';

\echo '=== QUALITY: missing EXCLDATE by state ==='
SELECT source_state, COUNT(*) FROM exclusion_main WHERE excldate = '' OR excldate IS NULL GROUP BY source_state ORDER BY 1;

\echo '=== QUALITY: cleaned_staging vs exclusion_main diff ==='
SELECT COUNT(*) AS staging_not_in_main FROM (
  SELECT lastname, firstname, npi, excldate, source_state FROM cleaned_staging
  EXCEPT
  SELECT lastname, firstname, npi, excldate, source_state FROM exclusion_main
) diff;

\echo '=== QUALITY: cross-state duplicate NPIs (top 5) ==='
SELECT npi, COUNT(DISTINCT source_state) AS states, array_agg(DISTINCT source_state ORDER BY source_state) AS state_list
FROM exclusion_main WHERE npi <> ''
GROUP BY npi HAVING COUNT(DISTINCT source_state) > 1
ORDER BY states DESC LIMIT 5;

\echo '=== SAMPLE: MD stage ==='
SELECT last_name_org, npi, termination_date FROM stage_maryland LIMIT 3;

\echo '=== SAMPLE: MI multi-date ==='
SELECT lastname, busname, excldate, excltype FROM cleaned_staging
WHERE source_state = 'MI' AND busname LIKE '%1st Priority%' ORDER BY excldate;

\echo '=== SAMPLE: exclusion_main first 5 ==='
SELECT lastname, busname, npi, excldate, source_state FROM exclusion_main ORDER BY id LIMIT 5;
SQL

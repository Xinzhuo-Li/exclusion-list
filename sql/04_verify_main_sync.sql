-- Verify exclusion_main strictly matches cleaned_staging (business columns only).
-- Run after merge. staging_minus_main and main_minus_staging should both be 0.
-- Sync compares 20 business columns only (not id, loaded_at). See docs/guides/MERGE_SEMANTICS.md

\echo '=== Row counts ==='
SELECT 'cleaned_staging' AS tbl, COUNT(*) FROM cleaned_staging
UNION ALL SELECT 'exclusion_main', COUNT(*) FROM exclusion_main;

\echo '=== By source_state ==='
SELECT source_state, COUNT(*) AS staging_cnt FROM cleaned_staging GROUP BY source_state ORDER BY 1;
SELECT source_state, COUNT(*) AS main_cnt FROM exclusion_main GROUP BY source_state ORDER BY 1;

\echo '=== Strict sync: rows in staging not in main (expect 0) ==='
SELECT COUNT(*) AS staging_minus_main FROM (
    SELECT lastname, firstname, midname, busname, general, specialty,
           upin, npi, dob, address, city, state, zip_code,
           excltype, excldate, reindate, waiverdate, waiverstate, list_source, source_state
    FROM cleaned_staging
    EXCEPT
    SELECT lastname, firstname, midname, busname, general, specialty,
           upin, npi, dob, address, city, state, zip_code,
           excltype, excldate, reindate, waiverdate, waiverstate, list_source, source_state
    FROM exclusion_main
) diff;

\echo '=== Strict sync: rows in main not in staging (expect 0) ==='
SELECT COUNT(*) AS main_minus_staging FROM (
    SELECT lastname, firstname, midname, busname, general, specialty,
           upin, npi, dob, address, city, state, zip_code,
           excltype, excldate, reindate, waiverdate, waiverstate, list_source, source_state
    FROM exclusion_main
    EXCEPT
    SELECT lastname, firstname, midname, busname, general, specialty,
           upin, npi, dob, address, city, state, zip_code,
           excltype, excldate, reindate, waiverdate, waiverstate, list_source, source_state
    FROM cleaned_staging
) diff;

\echo '=== Missing EXCLDATE (long-term exclusion; empty is valid) ==='
SELECT source_state, COUNT(*) FROM exclusion_main
WHERE excldate = '' GROUP BY source_state ORDER BY 1;

\echo '=== Cross-state duplicate NPIs (retained by policy) ==='
SELECT COUNT(*) AS npi_with_multiple_states FROM (
    SELECT npi FROM exclusion_main WHERE npi <> ''
    GROUP BY npi HAVING COUNT(DISTINCT source_state) > 1
) t;

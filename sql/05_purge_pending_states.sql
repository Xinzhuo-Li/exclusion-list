-- DEPRECATED — do not run on 39-state + LEIE production (2026-07+).
--
-- This script removed Austin 7 states during an early rollback when those states
-- were pending integration. Running it today would DELETE CA, NY, NC, ND, OH, NJ, PA
-- from exclusion_main and cleaned_staging.
--
-- Use sql/03_merge_to_main.sql for normal full refresh instead.

-- Remove withdrawn/pending colleague states from production tables.
-- Run after rollback when those states are not in cleaned_staging.

DELETE FROM exclusion_main
WHERE source_state IN ('CA', 'NY', 'NC', 'ND', 'OH', 'NJ', 'PA');

DELETE FROM cleaned_staging
WHERE source_state IN ('CA', 'NY', 'NC', 'ND', 'OH', 'NJ', 'PA');

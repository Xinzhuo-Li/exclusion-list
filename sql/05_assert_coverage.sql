-- Post-merge coverage assertion (run after 04_verify_main_sync.sql).
-- Fails the deploy if production coverage regresses (e.g. partial 6-state load).
-- See docs/guides/MERGE_SEMANTICS.md

\set ON_ERROR_STOP on

\echo '=== Coverage assertion (39 states + OIG) ==='

DO $$
DECLARE
    total_rows bigint;
    source_count bigint;
    state_rows bigint;
    federal_rows bigint;
BEGIN
    SELECT COUNT(*) INTO total_rows FROM exclusion_main;
    IF total_rows < 250000 THEN
        RAISE EXCEPTION 'exclusion_main row count too low: % (expected >= 250000)', total_rows;
    END IF;

    SELECT COUNT(DISTINCT source_state) INTO source_count FROM exclusion_main;
    IF source_count < 40 THEN
        RAISE EXCEPTION 'exclusion_main source_state count too low: % (expected 40)', source_count;
    END IF;

    SELECT COUNT(*) INTO state_rows FROM exclusion_main WHERE list_source = 'state';
    IF state_rows < 170000 THEN
        RAISE EXCEPTION 'state slice too small: % (expected >= 170000)', state_rows;
    END IF;

    SELECT COUNT(*) INTO federal_rows FROM exclusion_main WHERE list_source = 'federal';
    IF federal_rows < 80000 THEN
        RAISE EXCEPTION 'federal slice too small: % (expected >= 80000)', federal_rows;
    END IF;

    RAISE NOTICE 'Coverage OK: total=%, sources=%, state=%, federal=%',
        total_rows, source_count, state_rows, federal_rows;
END $$;

-- Idempotent migration: add list_source and widen source_state (safe on existing DBs).

ALTER TABLE exclusion_main
    ADD COLUMN IF NOT EXISTS list_source VARCHAR(10) NOT NULL DEFAULT 'state';

ALTER TABLE exclusion_main DROP CONSTRAINT IF EXISTS exclusion_main_list_source_check;
ALTER TABLE exclusion_main
    ADD CONSTRAINT exclusion_main_list_source_check
    CHECK (list_source IN ('federal', 'state'));

ALTER TABLE exclusion_main
    ALTER COLUMN source_state TYPE VARCHAR(10);

UPDATE exclusion_main SET list_source = 'state' WHERE list_source IS NULL OR list_source = '';

CREATE INDEX IF NOT EXISTS idx_exclusion_main_list_source ON exclusion_main (list_source);

ALTER TABLE cleaned_staging
    ADD COLUMN IF NOT EXISTS list_source VARCHAR(10) NOT NULL DEFAULT 'state';

ALTER TABLE cleaned_staging DROP CONSTRAINT IF EXISTS cleaned_staging_list_source_check;
ALTER TABLE cleaned_staging
    ADD CONSTRAINT cleaned_staging_list_source_check
    CHECK (list_source IN ('federal', 'state'));

ALTER TABLE cleaned_staging
    ALTER COLUMN source_state TYPE VARCHAR(10);

UPDATE cleaned_staging SET list_source = 'state' WHERE list_source IS NULL OR list_source = '';

CREATE INDEX IF NOT EXISTS idx_cleaned_staging_list_source ON cleaned_staging (list_source);

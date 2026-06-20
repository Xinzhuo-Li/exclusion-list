-- Main table: OIG LEIE 18 fields + source_state for merge tracking.
-- Text fields use TEXT to preserve full names from state source files.

CREATE TABLE IF NOT EXISTS exclusion_main (
    id SERIAL PRIMARY KEY,
    lastname TEXT,
    firstname TEXT,
    midname TEXT,
    busname TEXT,
    general TEXT,
    specialty TEXT,
    upin VARCHAR(6),
    npi VARCHAR(10),
    dob VARCHAR(8),
    address TEXT,
    city TEXT,
    state VARCHAR(2),
    zip_code VARCHAR(5),
    excltype TEXT,
    excldate VARCHAR(8),
    reindate VARCHAR(8),
    waiverdate VARCHAR(8),
    waiverstate VARCHAR(2),
    source_state CHAR(2) NOT NULL,
    loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exclusion_main_npi ON exclusion_main (npi);
CREATE INDEX IF NOT EXISTS idx_exclusion_main_source_state ON exclusion_main (source_state);
CREATE INDEX IF NOT EXISTS idx_exclusion_main_excldate ON exclusion_main (excldate);

-- Cleaned staging table loaded from data/cleaned/*.csv before merge.

CREATE TABLE IF NOT EXISTS cleaned_staging (
    id SERIAL PRIMARY KEY,
    lastname TEXT,
    firstname TEXT,
    midname TEXT,
    busname TEXT,
    general TEXT,
    specialty TEXT,
    upin VARCHAR(6),
    npi VARCHAR(10),
    dob VARCHAR(8),
    address TEXT,
    city TEXT,
    state VARCHAR(2),
    zip_code VARCHAR(5),
    excltype TEXT,
    excldate VARCHAR(8),
    reindate VARCHAR(8),
    waiverdate VARCHAR(8),
    waiverstate VARCHAR(2),
    source_state CHAR(2) NOT NULL,
    loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cleaned_staging_source_state ON cleaned_staging (source_state);

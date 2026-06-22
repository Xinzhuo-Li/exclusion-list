-- Main table: OIG LEIE 18 fields + source_state for merge tracking.
-- Leadership decision: TEXT fields preserve full names (no OIG truncation).
-- Empty CSV cells stored as '' (NOT NULL DEFAULT '').

DROP TABLE IF EXISTS exclusion_main CASCADE;
CREATE TABLE exclusion_main (
    id SERIAL PRIMARY KEY,
    lastname TEXT NOT NULL DEFAULT '',
    firstname TEXT NOT NULL DEFAULT '',
    midname TEXT NOT NULL DEFAULT '',
    busname TEXT NOT NULL DEFAULT '',
    general TEXT NOT NULL DEFAULT '',
    specialty TEXT NOT NULL DEFAULT '',
    upin VARCHAR(6) NOT NULL DEFAULT '',
    npi VARCHAR(10) NOT NULL DEFAULT '',
    dob VARCHAR(8) NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state VARCHAR(2) NOT NULL DEFAULT '',
    zip_code VARCHAR(5) NOT NULL DEFAULT '',
    excltype TEXT NOT NULL DEFAULT '',
    excldate VARCHAR(8) NOT NULL DEFAULT '',
    reindate VARCHAR(8) NOT NULL DEFAULT '',
    waiverdate VARCHAR(8) NOT NULL DEFAULT '',
    waiverstate VARCHAR(2) NOT NULL DEFAULT '',
    source_state CHAR(2) NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_exclusion_main_npi ON exclusion_main (npi);
CREATE INDEX idx_exclusion_main_source_state ON exclusion_main (source_state);
CREATE INDEX idx_exclusion_main_excldate ON exclusion_main (excldate);

-- Cleaned staging: must match exclusion_main column definitions (strict sync target).

DROP TABLE IF EXISTS cleaned_staging CASCADE;
CREATE TABLE cleaned_staging (
    id SERIAL PRIMARY KEY,
    lastname TEXT NOT NULL DEFAULT '',
    firstname TEXT NOT NULL DEFAULT '',
    midname TEXT NOT NULL DEFAULT '',
    busname TEXT NOT NULL DEFAULT '',
    general TEXT NOT NULL DEFAULT '',
    specialty TEXT NOT NULL DEFAULT '',
    upin VARCHAR(6) NOT NULL DEFAULT '',
    npi VARCHAR(10) NOT NULL DEFAULT '',
    dob VARCHAR(8) NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state VARCHAR(2) NOT NULL DEFAULT '',
    zip_code VARCHAR(5) NOT NULL DEFAULT '',
    excltype TEXT NOT NULL DEFAULT '',
    excldate VARCHAR(8) NOT NULL DEFAULT '',
    reindate VARCHAR(8) NOT NULL DEFAULT '',
    waiverdate VARCHAR(8) NOT NULL DEFAULT '',
    waiverstate VARCHAR(2) NOT NULL DEFAULT '',
    source_state CHAR(2) NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cleaned_staging_source_state ON cleaned_staging (source_state);

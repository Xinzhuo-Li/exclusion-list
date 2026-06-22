-- Merge cleaned_staging into exclusion_main (strict sync for six states).
-- Policy: full row copy of all business columns; no truncation; retain all NPI rows.
-- Idempotent: DELETE six states then INSERT from cleaned_staging.

DELETE FROM exclusion_main
WHERE source_state IN ('MD', 'MA', 'MI', 'MS', 'MT', 'NE');

INSERT INTO exclusion_main (
    lastname,
    firstname,
    midname,
    busname,
    general,
    specialty,
    upin,
    npi,
    dob,
    address,
    city,
    state,
    zip_code,
    excltype,
    excldate,
    reindate,
    waiverdate,
    waiverstate,
    source_state
)
SELECT
    lastname,
    firstname,
    midname,
    busname,
    general,
    specialty,
    upin,
    npi,
    dob,
    address,
    city,
    state,
    zip_code,
    excltype,
    excldate,
    reindate,
    waiverdate,
    waiverstate,
    source_state
FROM cleaned_staging
WHERE source_state IN ('MD', 'MA', 'MI', 'MS', 'MT', 'NE');

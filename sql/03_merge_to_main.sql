-- Merge cleaned staging records into the national exclusion_main table.
-- Run after validation passes and cleaned_staging is loaded.

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

-- Merge cleaned_staging into exclusion_main (strict sync by list_source + state).
-- Policy: full row copy of all business columns; no truncation; retain all NPI rows.
-- Idempotent: DELETE managed state rows then INSERT from cleaned_staging.

DELETE FROM exclusion_main
WHERE list_source = 'state'
  AND source_state IN (
    'MD', 'MA', 'MI', 'MS', 'MT', 'NE',
    'CA', 'NY', 'NC', 'ND', 'OH', 'NJ', 'PA',
    'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
    'AL', 'AK', 'AZ', 'AR', 'CO', 'CT', 'DE', 'DC', 'FL',
    'SC', 'TN', 'TX', 'VT', 'WA', 'WV', 'WY'
  );

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
    list_source,
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
    list_source,
    source_state
FROM cleaned_staging
WHERE list_source = 'state'
  AND source_state IN (
    'MD', 'MA', 'MI', 'MS', 'MT', 'NE',
    'CA', 'NY', 'NC', 'ND', 'OH', 'NJ', 'PA',
    'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
    'AL', 'AK', 'AZ', 'AR', 'CO', 'CT', 'DE', 'DC', 'FL',
    'SC', 'TN', 'TX', 'VT', 'WA', 'WV', 'WY'
  );

-- Federal LEIE (list_source = federal)
DELETE FROM exclusion_main WHERE list_source = 'federal';

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
    list_source,
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
    list_source,
    source_state
FROM cleaned_staging
WHERE list_source = 'federal';

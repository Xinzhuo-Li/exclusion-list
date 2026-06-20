-- Stage tables: one per state, preserving original source columns as TEXT.
-- Each row has id SERIAL PRIMARY KEY; empty CSV cells stored as '' (not NULL).

DROP TABLE IF EXISTS stage_maryland CASCADE;
CREATE TABLE stage_maryland (
    id SERIAL PRIMARY KEY,
    last_name_org TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    entity_type TEXT NOT NULL DEFAULT '',
    sanction_type TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    license_no TEXT NOT NULL DEFAULT '',
    termination_date TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    city_state_zip TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_massachusetts CASCADE;
CREATE TABLE stage_massachusetts (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    unique_id TEXT NOT NULL DEFAULT '',
    suspension_reason TEXT NOT NULL DEFAULT '',
    effective_date TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_michigan CASCADE;
CREATE TABLE stage_michigan (
    id SERIAL PRIMARY KEY,
    entity_name TEXT NOT NULL DEFAULT '',
    last_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    middle_name TEXT NOT NULL DEFAULT '',
    provider_category TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    license_no TEXT NOT NULL DEFAULT '',
    sanction_date1 TEXT NOT NULL DEFAULT '',
    sanction_source1 TEXT NOT NULL DEFAULT '',
    sanction_date2 TEXT NOT NULL DEFAULT '',
    sanction_source2 TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_mississippi CASCADE;
CREATE TABLE stage_mississippi (
    id SERIAL PRIMARY KEY,
    row_num TEXT NOT NULL DEFAULT '',
    provider_entity TEXT NOT NULL DEFAULT '',
    role TEXT NOT NULL DEFAULT '',
    org_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    last_name TEXT NOT NULL DEFAULT '',
    middle_name TEXT NOT NULL DEFAULT '',
    suffix TEXT NOT NULL DEFAULT '',
    address_line1 TEXT NOT NULL DEFAULT '',
    address_line2 TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    zipcode TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    medicaid_id TEXT NOT NULL DEFAULT '',
    date_of_birth TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    provider_specialty TEXT NOT NULL DEFAULT '',
    termination_effective_date TEXT NOT NULL DEFAULT '',
    termination_end_date TEXT NOT NULL DEFAULT '',
    exclusion_period TEXT NOT NULL DEFAULT '',
    termination_reason TEXT NOT NULL DEFAULT '',
    sanction_type TEXT NOT NULL DEFAULT '',
    additional_notes TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_montana CASCADE;
CREATE TABLE stage_montana (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL DEFAULT '',
    healthcare_profession TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    effective_date TEXT NOT NULL DEFAULT '',
    sanction_type TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_nebraska CASCADE;
CREATE TABLE stage_nebraska (
    id SERIAL PRIMARY KEY,
    date_added TEXT NOT NULL DEFAULT '',
    provider_name TEXT NOT NULL DEFAULT '',
    organization_name TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    effective_date TEXT NOT NULL DEFAULT '',
    provider_type_code TEXT NOT NULL DEFAULT '',
    reason_for_action TEXT NOT NULL DEFAULT '',
    sanction_code TEXT NOT NULL DEFAULT '',
    sanction_type_code TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

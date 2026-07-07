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

DROP TABLE IF EXISTS stage_north_carolina CASCADE;
CREATE TABLE stage_north_carolina (
    id SERIAL PRIMARY KEY,
    excluded_entity TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    exclusion_date TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    zip_code TEXT NOT NULL DEFAULT '',
    ownership TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_north_dakota CASCADE;
CREATE TABLE stage_north_dakota (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL DEFAULT '',
    business_name TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    zip_code TEXT NOT NULL DEFAULT '',
    medicaid_provider_num TEXT NOT NULL DEFAULT '',
    medicare_provider_num TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    license_number TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    practice_state TEXT NOT NULL DEFAULT '',
    sanction_type TEXT NOT NULL DEFAULT '',
    exclusion_date TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    verification_contact TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_ohio CASCADE;
CREATE TABLE stage_ohio (
    id SERIAL PRIMARY KEY,
    last_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    middle_name TEXT NOT NULL DEFAULT '',
    dob TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    provider_id TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT '',
    action_date TEXT NOT NULL DEFAULT '',
    date_added TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    record_type TEXT NOT NULL DEFAULT '',
    organization_name TEXT NOT NULL DEFAULT '',
    address_1 TEXT NOT NULL DEFAULT '',
    address_2 TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    zip_code TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_new_jersey CASCADE;
CREATE TABLE stage_new_jersey (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    street TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    zip_code TEXT NOT NULL DEFAULT '',
    action TEXT NOT NULL DEFAULT '',
    effective_date TEXT NOT NULL DEFAULT '',
    expiration_date TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_new_york CASCADE;
CREATE TABLE stage_new_york (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL DEFAULT '',
    license_num TEXT NOT NULL DEFAULT '',
    npi_num TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    exclusion_effective_date TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_pennsylvania CASCADE;
CREATE TABLE stage_pennsylvania (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL DEFAULT '',
    license_number TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT '',
    begin_date TEXT NOT NULL DEFAULT '',
    end_date TEXT NOT NULL DEFAULT '',
    cao TEXT NOT NULL DEFAULT '',
    list_date TEXT NOT NULL DEFAULT '',
    ind_chgd TEXT NOT NULL DEFAULT '',
    dte_change_last TEXT NOT NULL DEFAULT '',
    last_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    middle_name TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL DEFAULT '',
    suffix TEXT NOT NULL DEFAULT '',
    alt_name TEXT NOT NULL DEFAULT '',
    business_name TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    fein TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_california CASCADE;
CREATE TABLE stage_california (
    id SERIAL PRIMARY KEY,
    last_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    middle_name TEXT NOT NULL DEFAULT '',
    business_name TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    license_number TEXT NOT NULL DEFAULT '',
    provider_number TEXT NOT NULL DEFAULT '',
    exclusion_date TEXT NOT NULL DEFAULT '',
    active_period TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_georgia CASCADE;
CREATE TABLE stage_georgia (
    id SERIAL PRIMARY KEY,
    last_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    middle_name TEXT NOT NULL DEFAULT '',
    business_name TEXT NOT NULL DEFAULT '',
    general TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    exclusion_date TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_hawaii CASCADE;
CREATE TABLE stage_hawaii (
    id SERIAL PRIMARY KEY,
    last_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    middle_initial TEXT NOT NULL DEFAULT '',
    medicaid_provider_id TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    exclusion_date TEXT NOT NULL DEFAULT '',
    reinstatement_date TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_idaho CASCADE;
CREATE TABLE stage_idaho (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL DEFAULT '',
    start_date TEXT NOT NULL DEFAULT '',
    eligible_for_reinstatement TEXT NOT NULL DEFAULT '',
    date_reinstated TEXT NOT NULL DEFAULT '',
    additional_information TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_illinois CASCADE;
CREATE TABLE stage_illinois (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL DEFAULT '',
    license_number TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    action_date TEXT NOT NULL DEFAULT '',
    action_type TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    zip_code TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_indiana CASCADE;
CREATE TABLE stage_indiana (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    service_location TEXT NOT NULL DEFAULT '',
    termination_date TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_iowa CASCADE;
CREATE TABLE stage_iowa (
    id SERIAL PRIMARY KEY,
    enrollment_type TEXT NOT NULL DEFAULT '',
    specialty TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    affiliated_npi TEXT NOT NULL DEFAULT '',
    last_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    business_name TEXT NOT NULL DEFAULT '',
    sanction_type TEXT NOT NULL DEFAULT '',
    effective_date TEXT NOT NULL DEFAULT '',
    sanction_end_date TEXT NOT NULL DEFAULT '',
    eligible_reapply_date TEXT NOT NULL DEFAULT '',
    authority TEXT NOT NULL DEFAULT '',
    license_type TEXT NOT NULL DEFAULT '',
    license_number TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_kansas CASCADE;
CREATE TABLE stage_kansas (
    id SERIAL PRIMARY KEY,
    termination_date TEXT NOT NULL DEFAULT '',
    business_name TEXT NOT NULL DEFAULT '',
    provider_name TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    kmap_provider_number TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    comments TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_kentucky CASCADE;
CREATE TABLE stage_kentucky (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL DEFAULT '',
    last_name TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    license TEXT NOT NULL DEFAULT '',
    effective_date TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    timeframe TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_louisiana CASCADE;
CREATE TABLE stage_louisiana (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL DEFAULT '',
    last_name TEXT NOT NULL DEFAULT '',
    birthdate TEXT NOT NULL DEFAULT '',
    affiliated_entity TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    reason_exclusion TEXT NOT NULL DEFAULT '',
    period_exclusion TEXT NOT NULL DEFAULT '',
    reason_termination TEXT NOT NULL DEFAULT '',
    exclusion_type TEXT NOT NULL DEFAULT '',
    enrollment_prohibition_period TEXT NOT NULL DEFAULT '',
    effective_date TEXT NOT NULL DEFAULT '',
    reinstate_date TEXT NOT NULL DEFAULT '',
    state_zip TEXT NOT NULL DEFAULT '',
    program_office TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_maine CASCADE;
CREATE TABLE stage_maine (
    id SERIAL PRIMARY KEY,
    last_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    middle_initial TEXT NOT NULL DEFAULT '',
    alias_last_name_1 TEXT NOT NULL DEFAULT '',
    alias_first_name_1 TEXT NOT NULL DEFAULT '',
    alias_last_name_2 TEXT NOT NULL DEFAULT '',
    alias_first_name_2 TEXT NOT NULL DEFAULT '',
    alias_last_name_3 TEXT NOT NULL DEFAULT '',
    alias_first_name_3 TEXT NOT NULL DEFAULT '',
    alias_last_name_4 TEXT NOT NULL DEFAULT '',
    alias_first_name_4 TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    exclusion_start_date TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_alabama CASCADE;
CREATE TABLE stage_alabama (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL DEFAULT '',
    section TEXT NOT NULL DEFAULT '',
    suspension_date TEXT NOT NULL DEFAULT '',
    initiated_by TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_alaska CASCADE;
CREATE TABLE stage_alaska (
    id SERIAL PRIMARY KEY,
    exclusion_date TEXT NOT NULL DEFAULT '',
    last_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    exclusion_authority TEXT NOT NULL DEFAULT '',
    exclusion_reason TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_arizona CASCADE;
CREATE TABLE stage_arizona (
    id SERIAL PRIMARY KEY,
    npi TEXT NOT NULL DEFAULT '',
    provider_name TEXT NOT NULL DEFAULT '',
    exclusion_effective_date TEXT NOT NULL DEFAULT '',
    exclusion_end_date TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_arkansas CASCADE;
CREATE TABLE stage_arkansas (
    id SERIAL PRIMARY KEY,
    division TEXT NOT NULL DEFAULT '',
    facility_name TEXT NOT NULL DEFAULT '',
    provider_name TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    zip_code TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_colorado CASCADE;
CREATE TABLE stage_colorado (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL DEFAULT '',
    dba_name TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    termination_authority TEXT NOT NULL DEFAULT '',
    termination_effective_date TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_connecticut CASCADE;
CREATE TABLE stage_connecticut (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    business TEXT NOT NULL DEFAULT '',
    specialty TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    effective_date TEXT NOT NULL DEFAULT '',
    period TEXT NOT NULL DEFAULT '',
    administrative_action TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_delaware CASCADE;
CREATE TABLE stage_delaware (
    id SERIAL PRIMARY KEY,
    year TEXT NOT NULL DEFAULT '',
    provider_name TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    license_number TEXT NOT NULL DEFAULT '',
    dea_number TEXT NOT NULL DEFAULT '',
    sanction TEXT NOT NULL DEFAULT '',
    effective_date TEXT NOT NULL DEFAULT '',
    reinstated_date TEXT NOT NULL DEFAULT '',
    comments TEXT NOT NULL DEFAULT '',
    source_page TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_district_of_columbia CASCADE;
CREATE TABLE stage_district_of_columbia (
    id SERIAL PRIMARY KEY,
    lastname TEXT NOT NULL DEFAULT '',
    firstname TEXT NOT NULL DEFAULT '',
    midname TEXT NOT NULL DEFAULT '',
    busname TEXT NOT NULL DEFAULT '',
    general TEXT NOT NULL DEFAULT '',
    specialty TEXT NOT NULL DEFAULT '',
    upin TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    dob TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    zip_code TEXT NOT NULL DEFAULT '',
    excltype TEXT NOT NULL DEFAULT '',
    excldate TEXT NOT NULL DEFAULT '',
    reindate TEXT NOT NULL DEFAULT '',
    waiverdate TEXT NOT NULL DEFAULT '',
    waiverstate TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_florida CASCADE;
CREATE TABLE stage_florida (
    id SERIAL PRIMARY KEY,
    document_type TEXT NOT NULL DEFAULT '',
    provider TEXT NOT NULL DEFAULT '',
    ahca_case_number TEXT NOT NULL DEFAULT '',
    formal_case_number TEXT NOT NULL DEFAULT '',
    date_rendered TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_south_carolina CASCADE;
CREATE TABLE stage_south_carolina (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    zip_code TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    exclusion_status TEXT NOT NULL DEFAULT '',
    action_date TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_tennessee CASCADE;
CREATE TABLE stage_tennessee (
    id SERIAL PRIMARY KEY,
    last_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    effective_date TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_texas CASCADE;
CREATE TABLE stage_texas (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL DEFAULT '',
    last_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    mid_initial TEXT NOT NULL DEFAULT '',
    occupation TEXT NOT NULL DEFAULT '',
    license_number TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    start_date TEXT NOT NULL DEFAULT '',
    add_date TEXT NOT NULL DEFAULT '',
    reinstated_date TEXT NOT NULL DEFAULT '',
    eligible_reapply_date TEXT NOT NULL DEFAULT '',
    waiver TEXT NOT NULL DEFAULT '',
    web_comments TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_vermont CASCADE;
CREATE TABLE stage_vermont (
    id SERIAL PRIMARY KEY,
    provider_id TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    provider_name TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    address_state TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    exclusion_date TEXT NOT NULL DEFAULT '',
    exclusion_end_date TEXT NOT NULL DEFAULT '',
    reinstatement_date TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_washington CASCADE;
CREATE TABLE stage_washington (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    license_number TEXT NOT NULL DEFAULT '',
    npi TEXT NOT NULL DEFAULT '',
    exclusion_date TEXT NOT NULL DEFAULT '',
    action TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_west_virginia CASCADE;
CREATE TABLE stage_west_virginia (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    addresses TEXT NOT NULL DEFAULT '',
    identifiers TEXT NOT NULL DEFAULT '',
    sanctions TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS stage_wyoming CASCADE;
CREATE TABLE stage_wyoming (
    id SERIAL PRIMARY KEY,
    last_name TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    business_name TEXT NOT NULL DEFAULT '',
    provider_type TEXT NOT NULL DEFAULT '',
    provider_number TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    exclusion_date TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

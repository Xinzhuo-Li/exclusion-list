"""Load processed and cleaned CSV files into PostgreSQL."""

from __future__ import annotations

import csv
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

from src.config import (
    CLEANED_DIR,
    CLEANED_STATE_CODES,
    FEDERAL_CLEANED_FILE,
    PROCESSED_DIR,
    ROOT_DIR,
)
from src.load.merge_guard import assert_full_cleaned_load_scope

load_dotenv(ROOT_DIR / ".env")

STATE_STAGE_MAP = {
    "md": {
        "table": "stage_maryland",
        "file": "md_raw.csv",
        "columns": [
            "last_name_org",
            "first_name",
            "entity_type",
            "sanction_type",
            "npi",
            "license_no",
            "termination_date",
            "address",
            "city_state_zip",
        ],
    },
    "ma": {
        "table": "stage_massachusetts",
        "file": "ma_raw.csv",
        "columns": [
            "provider_name",
            "provider_type",
            "npi",
            "unique_id",
            "suspension_reason",
            "effective_date",
        ],
    },
    "mi": {
        "table": "stage_michigan",
        "file": "mi_raw.csv",
        "columns": [
            "entity_name",
            "last_name",
            "first_name",
            "middle_name",
            "provider_category",
            "npi",
            "city",
            "license_no",
            "sanction_date1",
            "sanction_source1",
            "sanction_date2",
            "sanction_source2",
            "reason",
        ],
    },
    "ms": {
        "table": "stage_mississippi",
        "file": "ms_raw.csv",
        "columns": [
            "row_num",
            "provider_entity",
            "role",
            "org_name",
            "first_name",
            "last_name",
            "middle_name",
            "suffix",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "zipcode",
            "npi",
            "medicaid_id",
            "date_of_birth",
            "provider_type",
            "provider_specialty",
            "termination_effective_date",
            "termination_end_date",
            "exclusion_period",
            "termination_reason",
            "sanction_type",
            "additional_notes",
        ],
    },
    "mt": {
        "table": "stage_montana",
        "file": "mt_raw.csv",
        "columns": [
            "provider_name",
            "healthcare_profession",
            "npi",
            "effective_date",
            "sanction_type",
        ],
    },
    "ne": {
        "table": "stage_nebraska",
        "file": "ne_raw.csv",
        "columns": [
            "date_added",
            "provider_name",
            "organization_name",
            "npi",
            "effective_date",
            "provider_type_code",
            "reason_for_action",
            "sanction_code",
            "sanction_type_code",
        ],
    },
    "nc": {
        "table": "stage_north_carolina",
        "file": "nc_raw.csv",
        "columns": [
            "excluded_entity",
            "npi",
            "exclusion_date",
            "reason",
            "city",
            "state",
            "zip_code",
            "ownership",
        ],
    },
    "nd": {
        "table": "stage_north_dakota",
        "file": "nd_raw.csv",
        "columns": [
            "provider_name",
            "business_name",
            "address",
            "city",
            "state",
            "zip_code",
            "medicaid_provider_num",
            "medicare_provider_num",
            "npi",
            "license_number",
            "provider_type",
            "practice_state",
            "sanction_type",
            "exclusion_date",
            "reason",
            "verification_contact",
        ],
    },
    "oh": {
        "table": "stage_ohio",
        "file": "oh_raw.csv",
        "columns": [
            "last_name",
            "first_name",
            "middle_name",
            "dob",
            "npi",
            "provider_id",
            "status",
            "action_date",
            "date_added",
            "provider_type",
            "record_type",
            "organization_name",
            "address_1",
            "address_2",
            "city",
            "state",
            "zip_code",
        ],
    },
    "nj": {
        "table": "stage_new_jersey",
        "file": "nj_raw.csv",
        "columns": [
            "provider_name",
            "title",
            "npi",
            "street",
            "city",
            "state",
            "zip_code",
            "action",
            "effective_date",
            "expiration_date",
        ],
    },
    "ny": {
        "table": "stage_new_york",
        "file": "ny_raw.csv",
        "columns": [
            "provider_name",
            "license_num",
            "npi_num",
            "provider_type",
            "exclusion_effective_date",
        ],
    },
    "pa": {
        "table": "stage_pennsylvania",
        "file": "pa_raw.csv",
        "columns": [
            "provider_name",
            "license_number",
            "status",
            "begin_date",
            "end_date",
            "cao",
            "list_date",
            "ind_chgd",
            "dte_change_last",
            "last_name",
            "first_name",
            "middle_name",
            "title",
            "suffix",
            "alt_name",
            "business_name",
            "npi",
            "fein",
        ],
    },
    "ca": {
        "table": "stage_california",
        "file": "ca_raw.csv",
        "columns": [
            "last_name",
            "first_name",
            "middle_name",
            "business_name",
            "address",
            "provider_type",
            "license_number",
            "provider_number",
            "exclusion_date",
            "active_period",
        ],
    },
    "ga": {
        "table": "stage_georgia",
        "file": "ga_raw.csv",
        "columns": [
            "last_name", "first_name", "middle_name", "business_name",
            "general", "state", "exclusion_date", "npi",
        ],
    },
    "hi": {
        "table": "stage_hawaii",
        "file": "hi_raw.csv",
        "columns": [
            "last_name", "first_name", "middle_initial", "medicaid_provider_id",
            "provider_type", "exclusion_date", "reinstatement_date", "state",
        ],
    },
    "id": {
        "table": "stage_idaho",
        "file": "id_raw.csv",
        "columns": [
            "full_name", "start_date", "eligible_for_reinstatement",
            "date_reinstated", "additional_information", "state",
        ],
    },
    "il": {
        "table": "stage_illinois",
        "file": "il_raw.csv",
        "columns": [
            "provider_name", "license_number", "npi", "provider_type",
            "action_date", "action_type", "address", "city", "state", "zip_code",
        ],
    },
    "in": {
        "table": "stage_indiana",
        "file": "in_raw.csv",
        "columns": ["provider_name", "npi", "service_location", "termination_date"],
    },
    "ia": {
        "table": "stage_iowa",
        "file": "ia_raw.csv",
        "columns": [
            "enrollment_type", "specialty", "npi", "affiliated_npi",
            "last_name", "first_name", "business_name", "sanction_type",
            "effective_date", "sanction_end_date", "eligible_reapply_date",
            "authority", "license_type", "license_number",
        ],
    },
    "ks": {
        "table": "stage_kansas",
        "file": "ks_raw.csv",
        "columns": [
            "termination_date", "business_name", "provider_name", "provider_type",
            "kmap_provider_number", "npi", "comments", "state",
        ],
    },
    "ky": {
        "table": "stage_kentucky",
        "file": "ky_raw.csv",
        "columns": [
            "first_name", "last_name", "npi", "license",
            "effective_date", "reason", "timeframe",
        ],
    },
    "la": {
        "table": "stage_louisiana",
        "file": "la_raw.csv",
        "columns": [
            "first_name", "last_name", "birthdate", "affiliated_entity",
            "provider_type", "npi", "reason_exclusion", "period_exclusion",
            "reason_termination", "exclusion_type", "enrollment_prohibition_period",
            "effective_date", "reinstate_date", "state_zip", "program_office", "state",
        ],
    },
    "me": {
        "table": "stage_maine",
        "file": "me_raw.csv",
        "columns": [
            "last_name", "first_name", "middle_initial",
            "alias_last_name_1", "alias_first_name_1",
            "alias_last_name_2", "alias_first_name_2",
            "alias_last_name_3", "alias_first_name_3",
            "alias_last_name_4", "alias_first_name_4",
            "provider_type", "exclusion_start_date", "state",
        ],
    },
    "al": {
        "table": "stage_alabama",
        "file": "al_raw.csv",
        "columns": ["provider_name", "section", "suspension_date", "initiated_by"],
    },
    "ak": {
        "table": "stage_alaska",
        "file": "ak_raw.csv",
        "columns": [
            "exclusion_date", "last_name", "first_name", "provider_type",
            "exclusion_authority", "exclusion_reason",
        ],
    },
    "az": {
        "table": "stage_arizona",
        "file": "az_raw.csv",
        "columns": ["npi", "provider_name", "exclusion_effective_date", "exclusion_end_date"],
    },
    "ar": {
        "table": "stage_arkansas",
        "file": "ar_raw.csv",
        "columns": ["division", "facility_name", "provider_name", "city", "state", "zip_code"],
    },
    "co": {
        "table": "stage_colorado",
        "file": "co_raw.csv",
        "columns": [
            "provider_name", "dba_name", "npi", "termination_authority",
            "termination_effective_date",
        ],
    },
    "ct": {
        "table": "stage_connecticut",
        "file": "ct_raw.csv",
        "columns": [
            "name", "business", "specialty", "address", "effective_date",
            "period", "administrative_action",
        ],
    },
    "de": {
        "table": "stage_delaware",
        "file": "de_raw.csv",
        "columns": [
            "year", "provider_name", "npi", "license_number", "dea_number",
            "sanction", "effective_date", "reinstated_date", "comments", "source_page",
        ],
    },
    "dc": {
        "table": "stage_district_of_columbia",
        "file": "dc_raw.csv",
        "columns": [
            "lastname", "firstname", "midname", "busname", "general", "specialty",
            "upin", "npi", "dob", "address", "city", "state", "zip_code",
            "excltype", "excldate", "reindate", "waiverdate", "waiverstate",
        ],
    },
    "fl": {
        "table": "stage_florida",
        "file": "fl_raw.csv",
        "columns": [
            "document_type", "provider", "ahca_case_number",
            "formal_case_number", "date_rendered",
        ],
    },
    "sc": {
        "table": "stage_south_carolina",
        "file": "sc_raw.csv",
        "columns": [
            "provider_name", "npi", "city", "state", "zip_code",
            "provider_type", "exclusion_status", "action_date",
        ],
    },
    "tn": {
        "table": "stage_tennessee",
        "file": "tn_raw.csv",
        "columns": ["last_name", "first_name", "npi", "effective_date", "reason"],
    },
    "tx": {
        "table": "stage_texas",
        "file": "tx_raw.csv",
        "columns": [
            "company_name", "last_name", "first_name", "mid_initial", "occupation",
            "license_number", "npi", "start_date", "add_date", "reinstated_date",
            "eligible_reapply_date", "waiver", "web_comments",
        ],
    },
    "vt": {
        "table": "stage_vermont",
        "file": "vt_raw.csv",
        "columns": [
            "provider_id", "npi", "provider_name", "provider_type", "city",
            "address_state", "reason", "exclusion_date", "exclusion_end_date",
            "reinstatement_date",
        ],
    },
    "wa": {
        "table": "stage_washington",
        "file": "wa_raw.csv",
        "columns": ["name", "license_number", "npi", "exclusion_date", "action"],
    },
    "wv": {
        "table": "stage_west_virginia",
        "file": "wv_raw.csv",
        "columns": ["provider_name", "provider_type", "addresses", "identifiers", "sanctions"],
    },
    "wy": {
        "table": "stage_wyoming",
        "file": "wy_raw.csv",
        "columns": [
            "last_name", "first_name", "business_name", "provider_type",
            "provider_number", "city", "state", "exclusion_date",
        ],
    },
}

CLEANED_COLUMNS = [
    "lastname",
    "firstname",
    "midname",
    "busname",
    "general",
    "specialty",
    "upin",
    "npi",
    "dob",
    "address",
    "city",
    "state",
    "zip_code",
    "excltype",
    "excldate",
    "reindate",
    "waiverdate",
    "waiverstate",
    "list_source",
    "source_state",
]


def get_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "exclusion_list"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
    )


def apply_migrations(conn) -> None:
    sql_path = ROOT_DIR / "sql" / "06_alter_add_list_source.sql"
    with sql_path.open(encoding="utf-8") as handle:
        with conn.cursor() as cur:
            cur.execute(handle.read())
    conn.commit()


def apply_schema(conn) -> None:
    for sql_file in (
        "01_create_stage_tables.sql",
        "02_create_main_table.sql",
    ):
        sql_path = ROOT_DIR / "sql" / sql_file
        with sql_path.open(encoding="utf-8") as handle:
            with conn.cursor() as cur:
                cur.execute(handle.read())
    conn.commit()
    apply_migrations(conn)


def truncate_table(conn, table_name: str) -> None:
    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY")
    conn.commit()


def _cell(value: str | None) -> str:
    """Coerce missing CSV values to empty string for NOT NULL columns."""
    if value is None:
        return ""
    return value


def load_csv_to_table(
    conn,
    csv_path: Path,
    table_name: str,
    columns: list[str],
) -> int:
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    rows: list[tuple[str, ...]] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(tuple(_cell(row.get(col)) for col in columns))

    if not rows:
        return 0

    placeholders = ", ".join(["%s"] * len(columns))
    column_sql = ", ".join(columns)
    sql = f"INSERT INTO {table_name} ({column_sql}) VALUES ({placeholders})"

    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    conn.commit()
    return len(rows)


def load_stage_data(conn, states: list[str] | None = None) -> dict[str, int]:
    selected = states or list(STATE_STAGE_MAP.keys())
    counts: dict[str, int] = {}
    for state in selected:
        config = STATE_STAGE_MAP[state]
        csv_path = PROCESSED_DIR / config["file"]
        truncate_table(conn, config["table"])
        counts[state] = load_csv_to_table(
            conn, csv_path, config["table"], config["columns"]
        )
    return counts


def load_cleaned_data(conn, states: list[str] | None = None) -> dict[str, int]:
    assert_full_cleaned_load_scope(states)
    selected = states or CLEANED_STATE_CODES
    truncate_table(conn, "cleaned_staging")
    counts: dict[str, int] = {}
    for state in selected:
        csv_path = CLEANED_DIR / f"{state}_oig.csv"
        count = load_csv_to_table(conn, csv_path, "cleaned_staging", CLEANED_COLUMNS)
        counts[state] = count
    federal_path = CLEANED_DIR / FEDERAL_CLEANED_FILE
    if federal_path.exists():
        counts["federal"] = load_csv_to_table(
            conn, federal_path, "cleaned_staging", CLEANED_COLUMNS
        )
    return counts


def run(states: list[str] | None = None, skip_schema: bool = False) -> None:
    with get_connection() as conn:
        if not skip_schema:
            apply_schema(conn)
        stage_counts = load_stage_data(conn, states)
        cleaned_counts = load_cleaned_data(conn, states)
        print("Stage load counts:", stage_counts)
        print("Cleaned load counts:", cleaned_counts)


if __name__ == "__main__":
    run()

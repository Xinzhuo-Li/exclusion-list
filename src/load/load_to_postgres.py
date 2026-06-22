"""Load processed and cleaned CSV files into PostgreSQL."""

from __future__ import annotations

import csv
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

from src.config import CLEANED_DIR, PROCESSED_DIR, ROOT_DIR

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
    selected = states or ["md", "ma", "mi", "ms", "mt", "ne"]
    truncate_table(conn, "cleaned_staging")
    counts: dict[str, int] = {}
    for state in selected:
        csv_path = CLEANED_DIR / f"{state}_oig.csv"
        count = load_csv_to_table(conn, csv_path, "cleaned_staging", CLEANED_COLUMNS)
        counts[state] = count
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

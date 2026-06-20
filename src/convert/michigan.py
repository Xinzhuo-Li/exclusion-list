"""Convert and clean Michigan exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import (
    build_oig_record,
    is_empty_row,
    normalize_text,
)
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed
from src.convert.michigan_dates import parse_michigan_date_field

SOURCE_STATE = "MI"
RAW_FILE = RAW_DIR / "Michigan.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, header=1)
    df = df.rename(
        columns={
            "Entity Name": "entity_name",
            "Last Name": "last_name",
            "First Name": "first_name",
            "Middle Name": "middle_name",
            "Provider Category": "provider_category",
            "NPI#": "npi",
            "City": "city",
            "License#": "license_no",
            "Sanction Date1": "sanction_date1",
            "Sanction Source": "sanction_source1",
            "Sanction Date2": "sanction_date2",
            "Sanction Source.1": "sanction_source2",
            "Reason": "reason",
        }
    )
    df = df.dropna(how="all")
    return df


def _build_identity(row: dict) -> dict[str, str]:
    entity_name = normalize_text(row.get("entity_name"))
    last_name = normalize_text(row.get("last_name"))
    first_name = normalize_text(row.get("first_name"))

    if last_name or first_name:
        return {
            "lastname": last_name,
            "firstname": first_name,
            "midname": normalize_text(row.get("middle_name")),
            "busname": entity_name,
        }

    return {
        "lastname": "",
        "firstname": "",
        "midname": "",
        "busname": entity_name,
    }


def _sanction_events(row: dict) -> list[tuple[str, str]]:
    """Expand Michigan sanction date fields into one event per parsed date."""
    events: list[tuple[str, str]] = []
    reason = normalize_text(row.get("reason"))
    source1 = normalize_text(row.get("sanction_source1")) or reason
    source2 = (
        normalize_text(row.get("sanction_source2"))
        or source1
        or reason
    )

    for parsed_date in parse_michigan_date_field(row.get("sanction_date1")):
        events.append((parsed_date, source1))

    for parsed_date in parse_michigan_date_field(row.get("sanction_date2")):
        events.append((parsed_date, source2))

    return events


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(
            row,
            [
                "entity_name",
                "last_name",
                "first_name",
                "npi",
                "sanction_date1",
                "sanction_date2",
            ],
        ):
            continue

        identity = _build_identity(row)
        events = _sanction_events(row)
        if not events:
            continue

        for excldate, excltype in events:
            records.append(
                build_oig_record(
                    source_state=SOURCE_STATE,
                    lastname=identity["lastname"],
                    firstname=identity["firstname"],
                    midname=identity["midname"],
                    busname=identity["busname"],
                    general=row.get("provider_category"),
                    npi=row.get("npi"),
                    city=row.get("city"),
                    state=SOURCE_STATE,
                    excltype=excltype,
                    excldate=excldate,
                    reindate="",
                )
            )
    return dedupe_records(records, state_code=SOURCE_STATE)


def run() -> tuple[pd.DataFrame, list[dict[str, str]]]:
    df = load_raw()
    records = to_oig_records(df)
    save_processed(df, SOURCE_STATE)
    save_cleaned(records, SOURCE_STATE)
    return df, records


if __name__ == "__main__":
    raw_df, cleaned = run()
    multi_date_rows = 0
    for row in raw_df.to_dict(orient="records"):
        count = len(_sanction_events(row))
        if count > 1:
            multi_date_rows += 1
    print(
        f"Michigan: {len(raw_df)} processed rows, {len(cleaned)} cleaned records "
        f"({multi_date_rows} source rows expanded to multiple sanctions)"
    )

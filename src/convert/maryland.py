"""Convert and clean Maryland exclusion list."""

from __future__ import annotations

import re

import pandas as pd

from src.clean.common import (
    build_oig_record,
    is_empty_row,
    normalize_text,
    parse_city_state_zip,
    resolve_name_fields,
)
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "MD"
RAW_FILE = RAW_DIR / "Maryland.xlsx"

PROCESSED_COLUMNS = {
    "LAST NAME/ORGANIZATION": "last_name_org",
    "FIRST NAME": "first_name",
    "TYPE OF ENTITY/PROFESSION": "entity_type",
    "SANCTION TYPE": "sanction_type",
    "NPI": "npi",
    "LICENSE NO": "license_no",
    "TERMINATION/SANCTION DATE": "termination_date",
    "ADDRESS": "address",
    "CITY/STATE/ZIP": "city_state_zip",
}

LEGEND_ROW_RE = re.compile(r"^[A-Z]+ = ")
FILE_STAMP_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


def is_metadata_row(row: dict) -> bool:
    text = normalize_text(row.get("last_name_org"))
    if not text:
        return True
    if LEGEND_ROW_RE.match(text):
        return True
    if FILE_STAMP_RE.fullmatch(text):
        return True
    return False


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, header=0)
    df = df.rename(columns=PROCESSED_COLUMNS)
    df = df.dropna(how="all")
    records = [row for row in df.to_dict(orient="records") if not is_metadata_row(row)]
    return pd.DataFrame(records)


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["last_name_org", "first_name", "npi"]):
            continue

        names = resolve_name_fields(
            last_name=row.get("last_name_org"),
            first_name=row.get("first_name"),
            provider_type=row.get("entity_type"),
        )
        if is_empty_row(names, ["lastname", "firstname", "busname"]):
            continue

        city, state, zip_code = parse_city_state_zip(row.get("city_state_zip"))

        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                general=row.get("entity_type"),
                npi=row.get("npi"),
                address=row.get("address"),
                city=city,
                state=state or SOURCE_STATE,
                zip_code=zip_code,
                excltype=row.get("sanction_type"),
                excldate=row.get("termination_date"),
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
    print(f"Maryland: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

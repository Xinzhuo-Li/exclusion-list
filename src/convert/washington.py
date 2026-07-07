"""Convert and clean Washington exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, extract_first_npi, is_empty_row, normalize_text, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "WA"
RAW_FILE = RAW_DIR / "Washington.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, skiprows=3).dropna(how="all")
    return df.rename(
        columns={
            "Name": "name",
            "License #": "license_number",
            "NPI # or P1 #": "npi",
            "Date of Exclusion": "exclusion_date",
            "Action": "action",
        }
    )


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        name = normalize_text(row.get("name")).replace("\n", " / ")
        if not name:
            continue
        names = resolve_name_fields(provider_name=name)
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                general=row.get("license_number"),
                npi=extract_first_npi(row.get("npi")),
                excltype=row.get("action"),
                excldate=row.get("exclusion_date"),
                state=SOURCE_STATE,
            )
        )
    return dedupe_records(records, state_code=SOURCE_STATE)


def run() -> tuple[pd.DataFrame, list[dict[str, str]]]:
    df = load_raw()
    records = to_oig_records(df)
    save_processed(df, SOURCE_STATE)
    save_cleaned(records, SOURCE_STATE)
    return df, records

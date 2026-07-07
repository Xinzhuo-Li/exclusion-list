"""Convert and clean Tennessee exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, extract_first_npi, is_empty_row, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "TN"
RAW_FILE = RAW_DIR / "Tennessee.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, skiprows=1).dropna(how="all")
    return df.rename(
        columns={
            "Last Name": "last_name",
            "First Name": "first_name",
            "NPI": "npi",
            "Effective Date": "effective_date",
            "Reason": "reason",
        }
    )


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["last_name", "first_name"]):
            continue
        names = resolve_name_fields(
            provider_name=f"{row.get('last_name')}, {row.get('first_name')}",
        )
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                npi=extract_first_npi(row.get("npi")),
                excltype=row.get("reason"),
                excldate=row.get("effective_date"),
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

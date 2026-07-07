"""Convert and clean Illinois exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, parse_combined_name, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "IL"
RAW_FILE = RAW_DIR / "Illinois.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, sheet_name="Active Sanctions")
    df = df.rename(
        columns={
            "Provider Name": "provider_name",
            "License #": "license_number",
            "NPI": "npi",
            "Provider Type": "provider_type",
            "Affiliation": "affiliation",
            "Action Date": "action_date",
            "Action Type": "action_type",
            "Address": "address",
            "Address2": "address2",
            "City": "city",
            "State": "state",
            "Zip Code": "zip_code",
        }
    )
    return df.drop(columns=["affiliation", "address2", "Address 2"], errors="ignore").dropna(how="all")


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["provider_name"]):
            continue
        names = parse_combined_name(row.get("provider_name"), row.get("provider_type"))
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                general=row.get("provider_type"),
                npi=row.get("npi"),
                address=row.get("address"),
                city=row.get("city"),
                state=row.get("state") or SOURCE_STATE,
                zip_code=row.get("zip_code"),
                excltype=row.get("action_type"),
                excldate=row.get("action_date"),
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
    print(f"Illinois: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

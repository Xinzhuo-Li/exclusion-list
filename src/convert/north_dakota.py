"""Convert and clean North Dakota exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import (
    build_oig_record,
    extract_first_npi,
    is_empty_row,
    resolve_name_fields,
)
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "ND"
RAW_FILE = RAW_DIR / "NorthDakota.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, header=4)
    df.columns = [
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
    ]
    return df.dropna(how="all")


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        names = resolve_name_fields(
            provider_name=row.get("provider_name"),
            business_name=row.get("business_name"),
            provider_type=row.get("provider_type"),
        )
        if is_empty_row(names, ["lastname", "firstname", "busname"]):
            continue
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                general=row.get("provider_type"),
                npi=extract_first_npi(row.get("npi")),
                address=row.get("address"),
                city=row.get("city"),
                state=row.get("state") or SOURCE_STATE,
                zip_code=row.get("zip_code"),
                excltype=row.get("reason"),
                excldate=row.get("exclusion_date"),
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
    print(f"North Dakota: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

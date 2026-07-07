"""Convert and clean Iowa exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "IA"
RAW_FILE = RAW_DIR / "Iowa.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, skiprows=1)
    df.columns = [
        "enrollment_type",
        "specialty",
        "npi",
        "affiliated_npi",
        "last_name",
        "first_name",
        "business_name",
        "sanction_type",
        "effective_date",
        "sanction_end_date",
        "eligible_reapply_date",
        "authority",
        "license_type",
        "license_number",
    ]
    return df.dropna(how="all")


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        names = resolve_name_fields(
            last_name=row.get("last_name"),
            first_name=row.get("first_name"),
            business_name=row.get("business_name"),
            provider_type=row.get("enrollment_type"),
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
                specialty=row.get("specialty"),
                npi=row.get("npi"),
                excltype=row.get("sanction_type"),
                excldate=row.get("effective_date"),
                reindate=row.get("sanction_end_date"),
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


if __name__ == "__main__":
    raw_df, cleaned = run()
    print(f"Iowa: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

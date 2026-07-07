"""Convert and clean Georgia exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "GA"
RAW_FILE = RAW_DIR / "Georgia.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, skiprows=2)
    df.columns = [
        "last_name",
        "first_name",
        "middle_name",
        "business_name",
        "general",
        "state",
        "exclusion_date",
        "npi",
        "extra",
    ]
    return df.drop(columns=["extra"], errors="ignore").dropna(how="all")


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["last_name", "first_name", "business_name"]):
            continue
        names = resolve_name_fields(
            last_name=row.get("last_name"),
            first_name=row.get("first_name"),
            mid_name=row.get("middle_name"),
            business_name=row.get("business_name"),
            provider_type=row.get("general"),
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
                general=row.get("general"),
                npi=row.get("npi"),
                state=row.get("state") or SOURCE_STATE,
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
    print(f"Georgia: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

"""Convert and clean Massachusetts exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import (
    build_oig_record,
    is_empty_row,
    parse_provider_name,
)
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "MA"
RAW_FILE = RAW_DIR / "Massachusetts.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, header=0)
    df = df.rename(
        columns={
            "Provider Name": "provider_name",
            "Provider Type": "provider_type",
            "National Provider Identifier (NPI)": "npi",
            "Unique ID": "unique_id",
            "Suspension/Exclusion Reason": "suspension_reason",
            "Suspension/Exclusion Effective Date": "effective_date",
        }
    )
    df = df.dropna(how="all")
    return df


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["provider_name", "npi", "effective_date"]):
            continue

        names = parse_provider_name(
            row.get("provider_name", ""),
            row.get("provider_type", ""),
        )
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                general=row.get("provider_type"),
                npi=row.get("npi"),
                state=SOURCE_STATE,
                excltype=row.get("suspension_reason"),
                excldate=row.get("effective_date"),
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
    print(f"Massachusetts: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

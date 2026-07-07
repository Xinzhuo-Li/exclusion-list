"""Convert and clean Delaware exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "DE"
RAW_FILE = RAW_DIR / "Delaware.csv"


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILE).dropna(how="all")
    return df.rename(
        columns={
            "Year": "year",
            "Sanctioned Provider Name": "provider_name",
            "NPI #": "npi",
            "License #": "license_number",
            "DEA #": "dea_number",
            "OIG / Medicaid Sanction": "sanction",
            "Effective Date": "effective_date",
            "Reinstated Date": "reinstated_date",
            "Comments": "comments",
            "Source Page": "source_page",
        }
    )


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["provider_name"]):
            continue
        names = resolve_name_fields(provider_name=row.get("provider_name"))
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                npi=row.get("npi"),
                general=row.get("license_number"),
                excltype=row.get("sanction"),
                excldate=row.get("effective_date"),
                reindate=row.get("reinstated_date"),
                specialty=row.get("comments"),
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
    print(f"Delaware: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

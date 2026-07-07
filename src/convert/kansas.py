"""Convert and clean Kansas exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "KS"
RAW_FILE = RAW_DIR / "Kansas.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, skiprows=1)
    df.columns = [
        "termination_date",
        "business_name",
        "provider_name",
        "provider_type",
        "kmap_provider_number",
        "npi",
        "comments",
    ]
    df["state"] = SOURCE_STATE
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
                npi=row.get("npi"),
                excltype=row.get("comments"),
                excldate=row.get("termination_date"),
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
    print(f"Kansas: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

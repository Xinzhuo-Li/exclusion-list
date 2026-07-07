"""Convert and clean Florida exclusion list (AHCA raw — use resolve_name_fields on Provider)."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "FL"
RAW_FILE = RAW_DIR / "Florida.csv"


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILE, low_memory=False).dropna(how="all")
    return df.rename(
        columns={
            "Document Type": "document_type",
            "Provider": "provider",
            "AHCA Case Number": "ahca_case_number",
            "Formal/Informal Case Number": "formal_case_number",
            "Date_Rendered": "date_rendered",
        }
    )


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["provider"]):
            continue
        names = resolve_name_fields(provider_name=row.get("provider"))
        if is_empty_row(names, ["lastname", "firstname", "busname"]):
            continue
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                general=row.get("ahca_case_number"),
                excltype=row.get("document_type"),
                excldate=row.get("date_rendered"),
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
    print(f"Florida: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

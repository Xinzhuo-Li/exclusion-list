"""Convert and clean North Carolina exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, extract_first_npi, is_empty_row, normalize_text
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "NC"
RAW_FILE = RAW_DIR / "NorthCarolina.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, header=6)
    df.columns = [
        "excluded_entity",
        "npi",
        "exclusion_date",
        "reason",
        "city",
        "state",
        "zip_code",
        "ownership",
    ]
    return df.dropna(how="all")


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["excluded_entity"]):
            continue
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                busname=row.get("excluded_entity"),
                npi=extract_first_npi(row.get("npi")),
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
    print(f"North Carolina: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

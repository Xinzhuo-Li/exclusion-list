"""Convert and clean Montana exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import (
    build_oig_record,
    is_empty_row,
    normalize_text,
    parse_alias_name,
    truncate_field,
)
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "MT"
RAW_FILE = RAW_DIR / "Montana.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, header=0)
    if "Unnamed: 4" in df.columns:
        df = df.rename(columns={"Unnamed: 4": "sanction_type"})
    df = df.rename(
        columns={
            "Terminated/Excluded Provider(s)": "provider_name",
            "Healthcare Profession": "healthcare_profession",
            "NPI": "npi",
            "Effective Date": "effective_date",
        }
    )
    df = df.dropna(how="all")
    return df


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["provider_name", "effective_date"]):
            continue

        provider_name = normalize_text(row.get("provider_name"))
        last, first, mid = parse_alias_name(provider_name)

        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=truncate_field("lastname", last),
                firstname=truncate_field("firstname", first),
                midname=truncate_field("midname", mid),
                general=row.get("healthcare_profession"),
                npi=row.get("npi"),
                state=SOURCE_STATE,
                excltype=row.get("sanction_type"),
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
    print(f"Montana: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

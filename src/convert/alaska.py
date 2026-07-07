"""Convert and clean Alaska exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, normalize_text, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "AK"
RAW_FILE = RAW_DIR / "Alaska.csv"


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILE).dropna(how="all")
    return df.rename(
        columns={
            "Exclusion Date": "exclusion_date",
            "Last Name": "last_name",
            "First Name": "first_name",
            "Provider Type": "provider_type",
            "Exclusion Authority": "exclusion_authority",
            "Exclusion Reason": "exclusion_reason",
        }
    )


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        last_name = normalize_text(row.get("last_name"))
        first_name = normalize_text(row.get("first_name"))
        if first_name in {"-", ""} and last_name:
            names = resolve_name_fields(provider_name=last_name, provider_type=row.get("provider_type"))
        else:
            names = resolve_name_fields(
                provider_name=f"{last_name}, {first_name}".strip(", "),
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
                excltype=row.get("exclusion_authority") or row.get("exclusion_reason"),
                excldate=row.get("exclusion_date"),
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
    print(f"Alaska: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

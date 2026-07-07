"""Convert and clean Colorado exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, parse_combined_name, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "CO"
RAW_FILE = RAW_DIR / "Colorado.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE).dropna(how="all")
    return df.rename(
        columns={
            "Provider Name": "provider_name",
            '"Doing Business As" Name': "dba_name",
            "NPI": "npi",
            "Termination Authority": "termination_authority",
            "Termination Effective Date": "termination_effective_date",
        }
    )


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["provider_name"]):
            continue
        provider = row.get("provider_name")
        if "," in str(provider):
            names = parse_combined_name(provider, row.get("dba_name"))
        else:
            names = resolve_name_fields(
                provider_name=provider,
                business_name=row.get("dba_name"),
            )
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                npi=row.get("npi"),
                excltype=row.get("termination_authority"),
                excldate=row.get("termination_effective_date"),
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
    print(f"Colorado: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

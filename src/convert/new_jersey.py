"""Convert and clean New Jersey exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import (
    build_oig_record,
    extract_first_npi,
    is_empty_row,
    normalize_text,
    parse_combined_name,
    truncate_field,
)
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "NJ"
RAW_FILE = RAW_DIR / "NewJersey.csv"


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILE, encoding="utf-8-sig").dropna(how="all")
    return df.rename(
        columns={
            "Provider Name": "provider_name",
            "Title": "title",
            "NPI": "npi",
            "Street": "street",
            "City": "city",
            "State": "state",
            "Zip": "zip_code",
            "Action": "action",
            "Effective Date": "effective_date",
            "Expiration Date": "expiration_date",
        }
    )


def _name_fields(provider_name: str) -> dict[str, str]:
    text = normalize_text(provider_name)
    if not text:
        return {"lastname": "", "firstname": "", "midname": "", "busname": ""}
    if "," in text:
        return parse_combined_name(text)
    return {
        "lastname": "",
        "firstname": "",
        "midname": "",
        "busname": truncate_field("busname", text),
    }


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["provider_name"]):
            continue
        names = _name_fields(row.get("provider_name"))
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                npi=extract_first_npi(row.get("npi")),
                address=normalize_text(row.get("street")).replace("\n", " "),
                city=row.get("city"),
                state=row.get("state") or SOURCE_STATE,
                zip_code=row.get("zip_code"),
                excltype=row.get("action"),
                excldate=row.get("effective_date"),
                reindate=row.get("expiration_date"),
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
    print(f"New Jersey: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

"""Convert and clean Connecticut exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, normalize_text, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "CT"
RAW_FILE = RAW_DIR / "Connecticut.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE).dropna(how="all")
    return df.rename(
        columns={
            "Name": "name",
            "Business": "business",
            "Specialty": "specialty",
            "Address": "address",
            "Effective Date": "effective_date",
            "Period": "period",
            "Administrative Action": "administrative_action",
        }
    )


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        name = normalize_text(row.get("name"))
        business = normalize_text(row.get("business"))
        if name in {"", ","} and not business:
            continue
        names = resolve_name_fields(
            provider_name=name if name not in {"", ","} else "",
            business_name=business,
            provider_type=row.get("specialty"),
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
                specialty=row.get("specialty"),
                address=row.get("address"),
                excltype=row.get("administrative_action"),
                excldate=row.get("effective_date"),
                general=row.get("period"),
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
    print(f"Connecticut: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

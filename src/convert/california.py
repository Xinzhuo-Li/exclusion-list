"""Convert and clean California exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import (
    build_oig_record,
    extract_first_npi,
    is_empty_row,
    normalize_text,
    parse_city_state_zip,
    resolve_name_fields,
)
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "CA"
RAW_FILE = RAW_DIR / "California.csv"


def _aka_column(columns: list[str]) -> str | None:
    for column in columns:
        if "Also Known" in column or column.startswith("A/K/A"):
            return column
    return None


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILE, encoding="utf-8-sig").dropna(how="all")
    aka_col = _aka_column(list(df.columns))
    rename_map = {
        "Last Name": "last_name",
        "First Name": "first_name",
        "Middle Name": "middle_name",
        "Address(es)": "address",
        "Provider Type": "provider_type",
        "License Number": "license_number",
        "Provider Number": "provider_number",
        "Date of Suspension": "exclusion_date",
        "Active Period": "active_period",
    }
    if aka_col:
        rename_map[aka_col] = "business_name"
    df = df.rename(columns=rename_map)
    drop_cols = [col for col in df.columns if col.startswith("Unnamed")]
    return df.drop(columns=drop_cols, errors="ignore")


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        raw_last = normalize_text(row.get("last_name"))
        raw_first = normalize_text(row.get("first_name"))
        raw_business = normalize_text(row.get("business_name"))
        if not raw_last and not raw_first and not raw_business:
            continue

        if not raw_first or raw_first.upper() == "N/A":
            names = resolve_name_fields(
                business_name=raw_last,
                provider_type=row.get("provider_type"),
                last_name_is_entity_column=True,
            )
        else:
            names = resolve_name_fields(
                last_name=raw_last,
                first_name=raw_first,
                mid_name=row.get("middle_name"),
                business_name="" if not raw_business or raw_business.upper() == "N/A" else raw_business,
                provider_type=row.get("provider_type"),
            )
        if is_empty_row(names, ["lastname", "firstname", "busname"]):
            continue

        address = normalize_text(row.get("address"))
        city, addr_state, zip_code = parse_city_state_zip(address)
        street = address
        if city or zip_code:
            for part in (city, addr_state, zip_code):
                if part and part in street:
                    street = street.replace(f", {part}", "").replace(part, "").strip(" ,")

        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                npi=extract_first_npi(row.get("provider_number")),
                general=row.get("provider_type"),
                address=street or address,
                city=city,
                state=addr_state or SOURCE_STATE,
                zip_code=zip_code,
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
    print(f"California: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

"""Convert and clean West Virginia exclusion list."""

from __future__ import annotations

import re

import pandas as pd

from src.clean.common import build_oig_record, extract_first_npi, is_empty_row, normalize_text, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "WV"
RAW_FILE = RAW_DIR / "WestVirginia.csv"


def _parse_address(value: str) -> tuple[str, str, str]:
    text = normalize_text(value)
    if not text:
        return "", SOURCE_STATE, ""
    match = re.search(r",\s*([^,]+),\s*([A-Z]{2})\s+(\d{5})", text)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return "", SOURCE_STATE, ""


def _extract_date(value: str) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    matches = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text)
    return matches[-1].replace("-", "") if matches else ""


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILE, dtype=str).dropna(how="all")
    return df.rename(
        columns={
            "name": "provider_name",
            "schema": "provider_type",
            "addresses": "addresses",
            "identifiers": "identifiers",
            "sanctions": "sanctions",
        }
    )


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["provider_name"]):
            continue
        names = resolve_name_fields(provider_name=row.get("provider_name"))
        city, addr_state, zip_code = _parse_address(row.get("addresses", ""))
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                general=row.get("provider_type"),
                npi=extract_first_npi(row.get("identifiers")),
                city=city,
                state=addr_state,
                zip_code=zip_code,
                excltype=row.get("sanctions"),
                excldate=_extract_date(row.get("sanctions", "")),
            )
        )
    return dedupe_records(records, state_code=SOURCE_STATE)


def run() -> tuple[pd.DataFrame, list[dict[str, str]]]:
    df = load_raw()
    records = to_oig_records(df)
    save_processed(df, SOURCE_STATE)
    save_cleaned(records, SOURCE_STATE)
    return df, records

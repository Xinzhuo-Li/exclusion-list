"""Convert and clean Wyoming exclusion list from PDF."""

from __future__ import annotations

import pandas as pd
import pdfplumber

from src.clean.common import build_oig_record, extract_first_npi, is_empty_row, normalize_text, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "WY"
RAW_FILE = RAW_DIR / "Wyoming.pdf"

TABLE_COLUMNS = [
    "last_name",
    "first_name",
    "business_name",
    "provider_type",
    "provider_number",
    "city",
    "state",
    "exclusion_date",
]


def _is_header_row(row: list[str | None]) -> bool:
    first = normalize_text(row[0] if row else "")
    joined = " ".join(normalize_text(cell) for cell in row if cell)
    if first.lower() == "last name":
        return True
    return "Wyoming Medicaid Provider Exclusion List" in joined


def load_raw() -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    with pdfplumber.open(RAW_FILE) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                for row in table:
                    if not row or not any(normalize_text(cell) for cell in row):
                        continue
                    if _is_header_row(row):
                        continue
                    padded = list(row) + [None] * max(0, len(TABLE_COLUMNS) - len(row))
                    rows.append(
                        {column: normalize_text(padded[index]) for index, column in enumerate(TABLE_COLUMNS)}
                    )
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("Wyoming PDF table extraction produced no rows.")
    return df


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["last_name", "first_name", "business_name"]):
            continue
        provider_name = ", ".join(
            part
            for part in [
                f"{row.get('last_name')}, {row.get('first_name')}".strip(", "),
                row.get("business_name"),
            ]
            if part and part.strip(", ")
        )
        names = resolve_name_fields(
            provider_name=provider_name,
            business_name=row.get("business_name"),
            provider_type=row.get("provider_type"),
        )
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                general=row.get("provider_type"),
                npi=extract_first_npi(row.get("provider_number")),
                city=row.get("city"),
                state=row.get("state") or SOURCE_STATE,
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

"""Convert and clean Alabama exclusion list (AmeeBeez raw — multi-section xlsx)."""

from __future__ import annotations

from datetime import datetime

import openpyxl
import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, parse_combined_name
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "AL"
RAW_FILE = RAW_DIR / "Alabama.xlsx"


def _is_section_header(value: object) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text or "," in text or text.startswith("http"):
        return False
    if "NAME OF PROVIDER" in text.upper() or "EFFECTIVE DATE" in text.upper():
        return False
    return text.isupper() and len(text) > 3


def load_raw() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    section = ""
    wb = openpyxl.load_workbook(RAW_FILE, read_only=True, data_only=True)
    ws = wb.active
    for row in ws.iter_rows(values_only=True):
        provider = row[0] if row else None
        effective = row[1] if row and len(row) > 1 else None
        initiated = row[2] if row and len(row) > 2 else None
        if provider is None and effective is None:
            continue
        if _is_section_header(provider):
            section = str(provider).strip()
            continue
        if not provider or not isinstance(effective, datetime):
            continue
        rows.append(
            {
                "provider_name": str(provider).strip(),
                "section": section,
                "suspension_date": effective,
                "initiated_by": str(initiated).strip() if initiated else "",
            }
        )
    wb.close()
    return pd.DataFrame(rows)


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["provider_name"]):
            continue
        names = parse_combined_name(row.get("provider_name"))
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                general=row.get("section"),
                excltype=row.get("initiated_by"),
                excldate=row.get("suspension_date"),
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
    print(f"Alabama: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

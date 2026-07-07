"""Convert and clean Maine exclusion list (PDF)."""

from __future__ import annotations

import re

import pandas as pd
import pdfplumber

from src.clean.common import build_oig_record, is_empty_row, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "ME"
RAW_FILE = RAW_DIR / "Maine.pdf"

COLUMNS = [
    "last_name",
    "first_name",
    "middle_initial",
    "alias_last_name_1",
    "alias_first_name_1",
    "alias_last_name_2",
    "alias_first_name_2",
    "alias_last_name_3",
    "alias_first_name_3",
    "alias_last_name_4",
    "alias_first_name_4",
    "provider_type",
    "exclusion_start_date",
]
NAME_COLUMNS = {c for c in COLUMNS if c not in ("provider_type", "exclusion_start_date")}


def _normalize_header(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _clean_cell(value: object, col_name: str) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text.upper() == "N/A" or text == "":
        return None
    if "\n" in text:
        parts = [p.strip() for p in text.split("\n") if p.strip()]
        text = "".join(parts) if col_name in NAME_COLUMNS else " ".join(parts)
    return re.sub(r"\s+", " ", text).strip() or None


def load_raw() -> pd.DataFrame:
    records: list[list[str | None]] = []
    with pdfplumber.open(RAW_FILE) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                for row in table:
                    if not row:
                        continue
                    if _normalize_header(row[0]).startswith("provider last name"):
                        continue
                    cells = list(row) + [None] * (len(COLUMNS) - len(row))
                    cells = cells[: len(COLUMNS)]
                    cleaned = [_clean_cell(cells[i], COLUMNS[i]) for i in range(len(COLUMNS))]
                    if not any(cleaned):
                        continue
                    records.append(cleaned)

    df = pd.DataFrame(records, columns=COLUMNS)
    df = df.dropna(how="all")
    df = df[df["last_name"].notna()]
    df["state"] = SOURCE_STATE
    return df


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["last_name"]):
            continue
        names = resolve_name_fields(
            last_name=row.get("last_name"),
            first_name=row.get("first_name"),
            mid_name=row.get("middle_initial"),
            provider_type=row.get("provider_type"),
            last_name_is_entity_column=True,
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
                excldate=row.get("exclusion_start_date"),
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
    print(f"Maine: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

"""Convert Nebraska exclusion list from PDF tables."""

from __future__ import annotations

import pandas as pd
import pdfplumber

from src.clean.common import (
    build_oig_record,
    is_empty_row,
    normalize_text,
    parse_provider_name,
    truncate_field,
)
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "NE"
RAW_FILE = RAW_DIR / "Nebraska.pdf"

TABLE_COLUMNS = [
    "date_added",
    "provider_name",
    "organization_name",
    "npi",
    "effective_date",
    "provider_type_code",
    "reason_for_action",
    "sanction_code",
    "sanction_type_code",
]


def _extract_tables(pdf_path) -> list[list[str | None]]:
    rows: list[list[str | None]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables() or []
            for table in tables:
                for row in table:
                    if not row or not any(normalize_text(cell) for cell in row):
                        continue
                    if normalize_text(row[0]).lower() == "date added to nmep":
                        continue
                    rows.append(row)
    return rows


def load_raw() -> pd.DataFrame:
    if not RAW_FILE.exists():
        raise FileNotFoundError(RAW_FILE)

    raw_rows = _extract_tables(RAW_FILE)
    normalized_rows = []
    for row in raw_rows:
        padded = list(row) + [None] * max(0, len(TABLE_COLUMNS) - len(row))
        normalized_rows.append(
            {
                column: normalize_text(padded[index])
                for index, column in enumerate(TABLE_COLUMNS)
            }
        )

    df = pd.DataFrame(normalized_rows)
    if df.empty:
        raise RuntimeError("Nebraska PDF table extraction produced no rows.")
    return df


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["provider_name", "organization_name", "effective_date"]):
            continue

        org_name = normalize_text(row.get("organization_name"))
        provider_name = normalize_text(row.get("provider_name"))
        provider_type = normalize_text(row.get("provider_type_code"))

        if org_name:
            names = {
                "lastname": "",
                "firstname": "",
                "midname": "",
                "busname": truncate_field("busname", org_name),
            }
            if provider_name:
                parsed = parse_provider_name(provider_name, provider_type)
                names["lastname"] = parsed["lastname"]
                names["firstname"] = parsed["firstname"]
                names["midname"] = parsed["midname"]
        else:
            names = parse_provider_name(provider_name, provider_type)

        excltype = normalize_text(row.get("sanction_code")) or normalize_text(
            row.get("reason_for_action")
        )

        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                general=provider_type,
                npi=row.get("npi"),
                state=SOURCE_STATE,
                excltype=excltype,
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
    print(f"Nebraska: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

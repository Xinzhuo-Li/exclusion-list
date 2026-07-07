"""Convert and clean Hawaii exclusion list (PDF)."""

from __future__ import annotations

import pandas as pd
import pdfplumber

from src.clean.common import build_oig_record, is_empty_row, normalize_text, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "HI"
RAW_FILE = RAW_DIR / "Hawaii.pdf"


def load_raw() -> pd.DataFrame:
    all_rows: list[list[str]] = []
    with pdfplumber.open(RAW_FILE) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                for row in table:
                    all_rows.append(row)

    header = all_rows[0]
    data_rows = [row for row in all_rows[1:] if row != header]
    df = pd.DataFrame(
        data_rows,
        columns=[
            "last_name",
            "first_name",
            "middle_initial",
            "medicaid_provider_id",
            "provider_type",
            "exclusion_date",
            "reinstatement_date",
        ],
    )
    df = df[df["last_name"] != "Last Name or Business Name"]
    df = df.dropna(how="all")
    df = df[df["last_name"].astype(str).str.strip() != ""]
    df["state"] = SOURCE_STATE
    return df


def _reindate(value: object) -> str:
    text = normalize_text(value)
    if not text or text.lower() == "indefinite":
        return ""
    return text


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
                excldate=row.get("exclusion_date"),
                reindate=_reindate(row.get("reinstatement_date")),
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
    print(f"Hawaii: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

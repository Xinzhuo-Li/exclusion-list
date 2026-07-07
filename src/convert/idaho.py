"""Convert and clean Idaho exclusion list (PDF)."""

from __future__ import annotations

import pandas as pd
import pdfplumber

from src.clean.common import build_oig_record, is_empty_row, parse_combined_name
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "ID"
RAW_FILE = RAW_DIR / "Idaho.pdf"


def load_raw() -> pd.DataFrame:
    all_rows: list[list[str]] = []
    with pdfplumber.open(RAW_FILE) as pdf:
        for page_num in range(1, len(pdf.pages)):
            page = pdf.pages[page_num]
            for table in page.extract_tables() or []:
                for row in table:
                    clean_row = [
                        cell for cell in row if cell is not None and str(cell).strip() != ""
                    ]
                    if clean_row:
                        all_rows.append(clean_row)

    all_rows = [r for r in all_rows if r[0] not in ("Name", "Date")]

    records: list[list[str | None]] = []
    for row in all_rows:
        name = str(row[0]).replace("\n", " ")
        start_date = row[1]
        eligible_date = row[2]
        if len(row) == 5:
            date_reinstated = row[3]
            info = str(row[4]).replace("\n", " ")
        else:
            date_reinstated = None
            info = str(row[3]).replace("\n", " ") if len(row) > 3 else None
        records.append([name, start_date, eligible_date, date_reinstated, info])

    df = pd.DataFrame(
        records,
        columns=[
            "full_name",
            "start_date",
            "eligible_for_reinstatement",
            "date_reinstated",
            "additional_information",
        ],
    )
    df["state"] = SOURCE_STATE
    return df


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["full_name"]):
            continue
        names = parse_combined_name(row.get("full_name"))
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                excltype=row.get("additional_information"),
                excldate=row.get("start_date"),
                reindate=row.get("date_reinstated"),
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
    print(f"Idaho: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

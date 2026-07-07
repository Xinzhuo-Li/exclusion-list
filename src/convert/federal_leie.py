"""Convert federal OIG LEIE database to OIG schema."""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from src.clean.common import build_oig_record, normalize_text
from src.config import CLEANED_DIR, FEDERAL_CLEANED_FILE, LIST_SOURCE_FEDERAL, OIG_COLUMNS, RAW_DIR

SOURCE_STATE = "OIG"
RAW_FILE = RAW_DIR / "LEIE.csv"
OUTPUT_FILE = CLEANED_DIR / FEDERAL_CLEANED_FILE


def load_raw() -> pd.DataFrame:
    return pd.read_csv(RAW_FILE, dtype=str, keep_default_na=False)


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        npi = normalize_text(row.get("NPI"))
        if npi == "0000000000":
            npi = ""
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                list_source=LIST_SOURCE_FEDERAL,
                lastname=row.get("LASTNAME"),
                firstname=row.get("FIRSTNAME"),
                midname=row.get("MIDNAME"),
                busname=row.get("BUSNAME"),
                general=row.get("GENERAL"),
                specialty=row.get("SPECIALTY"),
                upin=row.get("UPIN"),
                npi=npi,
                dob=row.get("DOB"),
                address=row.get("ADDRESS"),
                city=row.get("CITY"),
                state=row.get("STATE"),
                zip_code=row.get("ZIP"),
                excltype=row.get("EXCLTYPE"),
                excldate=row.get("EXCLDATE"),
                reindate=row.get("REINDATE"),
                waiverdate=row.get("WAIVERDATE"),
                waiverstate=row.get("WVRSTATE"),
            )
        )
    return records


def save_federal_cleaned(records: list[dict[str, str]]) -> Path:
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = OIG_COLUMNS + ["source_state"]
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({key: record.get(key, "") for key in fieldnames})
    return OUTPUT_FILE


def run() -> tuple[pd.DataFrame, list[dict[str, str]]]:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Federal LEIE source not found: {RAW_FILE}")
    df = load_raw()
    records = to_oig_records(df)
    save_federal_cleaned(records)
    processed_dir = Path(CLEANED_DIR).parent / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_dir / "federal_raw.csv", index=False)
    return df, records


if __name__ == "__main__":
    raw_df, cleaned = run()
    print(f"Federal LEIE: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

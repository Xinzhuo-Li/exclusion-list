"""Convert and clean Vermont exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, extract_first_npi, is_empty_row, parse_combined_name
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "VT"
RAW_FILE = RAW_DIR / "Vermont.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, skiprows=1).dropna(how="all")
    df = df.rename(
        columns={
            "VT Medicaid Provider ID ": "provider_id",
            "Provider NPI": "npi",
            "Provider Full Name": "provider_name",
            "Provider Type ": "provider_type",
            "Provider City": "city",
            "State": "address_state",
            "Reason or \"Cause\" for Exclusion": "reason",
            "Provider Exclusion Status Effective Date": "exclusion_date",
            "Provider Exclusion Status End Date": "exclusion_end_date",
            "Reinstatement Date with Vermont Medicaid if Applicable": "reinstatement_date",
        }
    )
    return df[[
        "provider_id", "npi", "provider_name", "provider_type", "city",
        "address_state", "reason", "exclusion_date", "exclusion_end_date",
        "reinstatement_date",
    ]]


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
                general=row.get("provider_type"),
                npi=extract_first_npi(row.get("npi")),
                city=row.get("city"),
                excltype=row.get("reason"),
                excldate=row.get("exclusion_date"),
                reindate=row.get("reinstatement_date"),
                state=row.get("address_state") or SOURCE_STATE,
            )
        )
    return dedupe_records(records, state_code=SOURCE_STATE)


def run() -> tuple[pd.DataFrame, list[dict[str, str]]]:
    df = load_raw()
    records = to_oig_records(df)
    save_processed(df, SOURCE_STATE)
    save_cleaned(records, SOURCE_STATE)
    return df, records

"""Convert and clean Pennsylvania exclusion list."""

from __future__ import annotations

import re

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, normalize_text, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "PA"
RAW_FILE = RAW_DIR / "Pennsylvania.csv"


def parse_pa_cao_state(cao: object) -> str:
    """Return address state: PA counties default to PA; out-of-state parses (XX) code."""
    text = normalize_text(cao)
    if not text:
        return SOURCE_STATE
    upper = text.upper()
    if "OUT OF STATE" in upper or "OUT-OF-STATE" in upper:
        match = re.search(r"\(([A-Z]{2})\)", upper)
        if match:
            return match.group(1)
        return ""
    return SOURCE_STATE


def pa_reindate_for_status(status: object, end_date: object) -> str:
    """Only Reinstated providers get a reinstatement date."""
    if normalize_text(status).upper() == "REINSTATED":
        return normalize_text(end_date)
    return ""


def load_raw() -> pd.DataFrame:
    return pd.read_csv(RAW_FILE, encoding="utf-8-sig").dropna(how="all").rename(
        columns={
            "ProviderName": "provider_name",
            "LicenseNumber": "license_number",
            "Status": "status",
            "BeginDate": "begin_date",
            "EndDate": "end_date",
            "CAO": "cao",
            "ListDate": "list_date",
            "IND_CHGD": "ind_chgd",
            "DTE_CHANGE_LAST": "dte_change_last",
            "NAM_LAST_PROVR": "last_name",
            "NAM_FIRST_PROVR": "first_name",
            "NAM_MIDDLE_PROVR": "middle_name",
            "NAM_TITLE_PROVR": "title",
            "NAM_SUFFIX_PROVR": "suffix",
            "NAM_PROVR_ALT": "alt_name",
            "NAM_BUSNS_MP": "business_name",
            "IDN_NPI": "npi",
            "NBR_FEIN": "fein",
        }
    )


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        names = resolve_name_fields(
            last_name=row.get("last_name"),
            first_name=row.get("first_name"),
            mid_name=row.get("middle_name"),
            business_name=row.get("business_name"),
            provider_name=row.get("provider_name"),
            provider_type=row.get("title"),
        )
        if is_empty_row(names, ["lastname", "firstname", "busname"]):
            continue
        addr_state = parse_pa_cao_state(row.get("cao"))
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                npi=row.get("npi"),
                excltype=row.get("status"),
                excldate=row.get("begin_date"),
                reindate=pa_reindate_for_status(row.get("status"), row.get("end_date")),
                state=addr_state,
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
    print(f"Pennsylvania: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

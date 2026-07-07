"""Convert and clean Texas exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, extract_first_npi, is_empty_row, normalize_text, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "TX"
RAW_FILE = RAW_DIR / "Texas.xls"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, engine="xlrd").dropna(how="all")
    return df.rename(
        columns={
            "CompanyName": "company_name",
            "LastName": "last_name",
            "FirstName": "first_name",
            "MidInitial": "mid_initial",
            "Occupation": "occupation",
            "LicenseNumber": "license_number",
            "NPI": "npi",
            "StartDate": "start_date",
            "AddDate": "add_date",
            "ReinstatedDate": "reinstated_date",
            "EligibleToReapplyDate": "eligible_reapply_date",
            "Waiver": "waiver",
            "WebComments": "web_comments",
        }
    )


def _provider_name(row: dict) -> str:
    company = normalize_text(row.get("company_name"))
    last = normalize_text(row.get("last_name"))
    first = normalize_text(row.get("first_name"))
    mid = normalize_text(row.get("mid_initial"))
    if company and not last and not first:
        return company
    if last and first:
        person = f"{last}, {first}"
        if mid:
            person = f"{person} {mid}"
        return f"{company} / {person}" if company else person
    return company or last or first


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        provider = _provider_name(row)
        if not provider:
            continue
        names = resolve_name_fields(provider_name=provider, provider_type=row.get("occupation"))
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                general=row.get("occupation"),
                npi=extract_first_npi(row.get("npi")),
                excltype=row.get("web_comments"),
                excldate=row.get("start_date") or row.get("add_date"),
                reindate=row.get("reinstated_date"),
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

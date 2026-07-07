"""Convert and clean Ohio exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, extract_first_npi, is_empty_row, normalize_text
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "OH"
RAW_FILE = RAW_DIR / "Ohio.xlsx"


def _zip_value(value) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    try:
        return str(int(float(text)))
    except (TypeError, ValueError):
        return text


def load_raw() -> pd.DataFrame:
    individuals = pd.read_excel(RAW_FILE, sheet_name="Individuals")
    organizations = pd.read_excel(RAW_FILE, sheet_name="Organizations")
    individuals = individuals.assign(record_type="individual")
    organizations = organizations.assign(record_type="organization")
    combined = pd.concat([individuals, organizations], ignore_index=True, sort=False)
    combined = combined.rename(
        columns={
            "Last Name": "last_name",
            "First Name": "first_name",
            "Middle Name": "middle_name",
            "DOB": "dob",
            "NPI": "npi",
            "Provider ID": "provider_id",
            "Status": "status",
            "Action Date": "action_date",
            "Date Added": "date_added",
            "Provider Type": "provider_type",
            "Organization Name": "organization_name",
            "Address 1": "address_1",
            "Address 2": "address_2",
            "City": "city",
            "State": "state",
            "Zip Code": "zip_code",
        }
    )
    return combined


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if row.get("record_type") == "organization":
            name = normalize_text(row.get("organization_name"))
            if not name:
                continue
            records.append(
                build_oig_record(
                    source_state=SOURCE_STATE,
                    busname=name,
                    npi=extract_first_npi(row.get("npi")),
                    address=row.get("address_1"),
                    city=row.get("city"),
                    state=row.get("state") or SOURCE_STATE,
                    zip_code=_zip_value(row.get("zip_code")),
                    general=row.get("provider_type"),
                    excltype=row.get("status"),
                    excldate=row.get("action_date"),
                )
            )
            continue

        if is_empty_row(row, ["last_name", "first_name"]):
            continue
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=row.get("last_name"),
                firstname=row.get("first_name"),
                midname=row.get("middle_name"),
                dob=row.get("dob"),
                npi=extract_first_npi(row.get("npi")),
                general=row.get("provider_type"),
                excltype=row.get("status"),
                excldate=row.get("action_date"),
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
    print(f"Ohio: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

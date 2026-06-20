"""Convert and clean Mississippi exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, normalize_reindate, normalize_text, truncate_field
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "MS"
RAW_FILE = RAW_DIR / "Mississippi.xlsx"


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "#": "row_num",
        "Provider Entity \n(Org/Ind)": "provider_entity",
        "Role": "role",
        "Provider Organization Name\n (Applicable for Organizations Only)": "org_name",
        "Provider First Name\n(Applicable for Individuals Only)": "first_name",
        "Provider Last Name\n(Applicable for Individuals Only)": "last_name",
        "Provider MI Name\n(Applicable for Individuals Only)": "middle_name",
        "Provider Suffix Name\n(Applicable for Individuals Only)": "suffix",
        "Provider Address Line 12": "address_line1",
        "Provider Address Line 2 ": "address_line2",
        "City": "city",
        "State": "state",
        "Zipcode": "zipcode",
        "NPI": "npi",
        "Medicaid ID": "medicaid_id",
        "Date of Birth": "date_of_birth",
        "Provider Type": "provider_type",
        "Provider Speciality ": "provider_specialty",
        "Termination Effective Date": "termination_effective_date",
        "Termination End Date": "termination_end_date",
        "Exclusion Period": "exclusion_period",
        "Termination Reason": "termination_reason",
        "Sanction Type": "sanction_type",
        "Additional Notes ": "additional_notes",
    }
    return df.rename(columns=rename_map)


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, header=8)
    df = _normalize_columns(df)
    df = df.dropna(how="all")

    has_row_num = df["row_num"].notna()
    has_provider_data = df.apply(
        lambda row: bool(
            normalize_text(row.get("last_name"))
            or normalize_text(row.get("org_name"))
            or normalize_text(row.get("npi"))
        )
        and bool(normalize_text(row.get("termination_effective_date"))),
        axis=1,
    )
    df = df[has_row_num | has_provider_data]
    return df


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(
            row,
            ["org_name", "first_name", "last_name", "npi", "termination_effective_date"],
        ):
            continue

        entity = normalize_text(row.get("provider_entity")).upper()
        address_parts = [
            normalize_text(row.get("address_line1")),
            normalize_text(row.get("address_line2")),
        ]
        address = " ".join(part for part in address_parts if part)

        if entity == "ORGANIZATION":
            busname = truncate_field("busname", row.get("org_name"))
            lastname = ""
            firstname = ""
            midname = ""
        else:
            busname = truncate_field("busname", row.get("org_name"))
            lastname = truncate_field("lastname", row.get("last_name"))
            firstname = truncate_field("firstname", row.get("first_name"))
            midname = truncate_field("midname", row.get("middle_name"))

        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=lastname,
                firstname=firstname,
                midname=midname,
                busname=busname,
                general=row.get("provider_type"),
                specialty=row.get("provider_specialty"),
                npi=row.get("npi"),
                dob=row.get("date_of_birth"),
                address=address,
                city=row.get("city"),
                state=row.get("state") or SOURCE_STATE,
                zip_code=row.get("zipcode"),
                excltype=row.get("sanction_type"),
                excldate=row.get("termination_effective_date"),
                reindate=normalize_reindate(
                    row.get("termination_end_date"),
                    row.get("exclusion_period"),
                ),
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
    print(f"Mississippi: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

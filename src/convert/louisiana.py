"""Convert and clean Louisiana exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, normalize_text, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "LA"
RAW_FILE = RAW_DIR / "Louisiana.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, skiprows=1)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(
        columns={
            "First Name": "first_name",
            "Last Name or Entity Name": "last_name",
            "Birthdate": "birthdate",
            "Affiliated Entity": "affiliated_entity",
            "Title or Provider Type": "provider_type",
            "NPI#": "npi",
            "Reason for Exclusion": "reason_exclusion",
            "Period of Exclusion": "period_exclusion",
            "Reason for Termination": "reason_termination",
            "Type of Exclusion": "exclusion_type",
            "Period of Enrollment Prohibition": "enrollment_prohibition_period",
            "Effective Date": "effective_date",
            "Reinstate": "reinstate_date",
            "State and Zip": "state_zip",
            "Program Office": "program_office",
        }
    )
    df["state"] = SOURCE_STATE
    return df.dropna(how="all")


def _excltype(row: dict) -> str:
    parts = [
        normalize_text(row.get("reason_exclusion")),
        normalize_text(row.get("reason_termination")),
    ]
    return " ".join(p for p in parts if p)


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        names = resolve_name_fields(
            last_name=row.get("last_name"),
            first_name=row.get("first_name"),
            business_name=row.get("affiliated_entity"),
            provider_type=row.get("provider_type"),
            last_name_is_entity_column=True,
            split_multi_given_first_names=True,
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
                npi=row.get("npi"),
                dob=row.get("birthdate"),
                excltype=_excltype(row),
                excldate=row.get("effective_date"),
                reindate=row.get("reinstate_date"),
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
    print(f"Louisiana: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

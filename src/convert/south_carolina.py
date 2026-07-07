"""Convert and clean South Carolina exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, extract_first_npi, is_empty_row, normalize_text, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "SC"
RAW_FILE = RAW_DIR / "SouthCarolina.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, skiprows=2).dropna(how="all")
    return df.rename(
        columns={
            "Individual//Entity": "provider_name",
            "NPI": "npi",
            "City": "city",
            "State": "state",
            "Zip": "zip_code",
            "Last Known Profession/Provider Type": "provider_type",
            "Excluded/Terminated": "exclusion_status",
            "Action Date": "action_date",
        }
    )


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["provider_name"]):
            continue
        names = resolve_name_fields(provider_name=row.get("provider_name"), provider_type=row.get("provider_type"))
        npi_raw = normalize_text(row.get("npi"))
        npi = "" if npi_raw.lower() in {"not found", "n/a", "na"} else extract_first_npi(npi_raw)
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
                general=row.get("provider_type"),
                npi=npi,
                city=row.get("city"),
                state=row.get("state") or SOURCE_STATE,
                zip_code=row.get("zip_code"),
                excltype=f"{row.get('exclusion_status') or ''}".strip(),
                excldate=row.get("action_date"),
            )
        )
    return dedupe_records(records, state_code=SOURCE_STATE)


def run() -> tuple[pd.DataFrame, list[dict[str, str]]]:
    df = load_raw()
    records = to_oig_records(df)
    save_processed(df, SOURCE_STATE)
    save_cleaned(records, SOURCE_STATE)
    return df, records

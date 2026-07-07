"""Convert and clean District of Columbia exclusion list (OIG-shaped raw)."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, normalize_text
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "DC"
RAW_FILE = RAW_DIR / "DistrictOfColumbia.csv"


def _clean_value(value: object) -> str:
    text = normalize_text(value)
    if text in {"0", "0000000000"}:
        return ""
    return text


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILE).dropna(how="all")
    return df.rename(
        columns={
            "LASTNAME": "lastname",
            "FIRSTNAME": "firstname",
            "MIDNAME": "midname",
            "BUSNAME": "busname",
            "GENERAL": "general",
            "SPECIALTY": "specialty",
            "UPIN": "upin",
            "NPI": "npi",
            "DOB": "dob",
            "ADDRESS": "address",
            "CITY": "city",
            "STATE": "state",
            "ZIP": "zip_code",
            "EXCLTYPE": "excltype",
            "EXCLDATE": "excldate",
            "REINDATE": "reindate",
            "WAIVERDATE": "waiverdate",
            "WVRSTATE": "waiverstate",
        }
    )


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        if is_empty_row(row, ["lastname", "firstname", "busname"]):
            continue
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=row.get("lastname"),
                firstname=row.get("firstname"),
                midname=row.get("midname"),
                busname=row.get("busname"),
                general=row.get("general"),
                specialty=row.get("specialty"),
                upin=_clean_value(row.get("upin")),
                npi=_clean_value(row.get("npi")),
                dob=_clean_value(row.get("dob")),
                address=row.get("address"),
                city=row.get("city"),
                state=row.get("state") or SOURCE_STATE,
                zip_code=row.get("zip_code"),
                excltype=row.get("excltype"),
                excldate=_clean_value(row.get("excldate")),
                reindate=_clean_value(row.get("reindate")),
                waiverdate=_clean_value(row.get("waiverdate")),
                waiverstate=row.get("waiverstate"),
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
    print(f"District of Columbia: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

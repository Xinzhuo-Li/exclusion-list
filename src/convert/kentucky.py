"""Convert and clean Kentucky exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, normalize_text, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "KY"
RAW_FILE = RAW_DIR / "Kentucky.xlsx"


def load_raw() -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, skiprows=2)
    df.columns = [
        "first_name",
        "last_name",
        "npi",
        "license",
        "effective_date",
        "reason",
        "timeframe",
    ]
    return df.dropna(how="all")


def _excltype(reason: object, timeframe: object) -> str:
    parts = [normalize_text(reason), normalize_text(timeframe)]
    return " ".join(p for p in parts if p)


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        names = resolve_name_fields(
            last_name=row.get("last_name"),
            first_name=row.get("first_name"),
            provider_type=row.get("reason"),
            last_name_is_entity_column=True,
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
                npi=row.get("npi"),
                excltype=_excltype(row.get("reason"), row.get("timeframe")),
                excldate=row.get("effective_date"),
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
    print(f"Kentucky: {len(raw_df)} processed rows, {len(cleaned)} cleaned records")

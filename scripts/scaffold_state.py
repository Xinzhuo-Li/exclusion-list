#!/usr/bin/env python3
"""Scaffold a new state convert module using project conventions.

Usage:
  python3 scripts/scaffold_state.py TX texas Texas.xlsx
  python3 scripts/scaffold_state.py FL florida Florida.pdf --entity-column
"""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONVERT_DIR = ROOT / "src" / "convert"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold src/convert/{state}.py")
    parser.add_argument("state_code", help="Two-letter code, e.g. TX")
    parser.add_argument("module_name", help="Python module name, e.g. texas")
    parser.add_argument("raw_filename", help="File under data/raw/, e.g. Texas.xlsx")
    parser.add_argument(
        "--entity-column",
        action="store_true",
        help="Set last_name_is_entity_column=True in resolve_name_fields",
    )
    parser.add_argument(
        "--multi-given-first",
        action="store_true",
        help="Set split_multi_given_first_names=True (LA-style)",
    )
    parser.add_argument(
        "--combined-name",
        action="store_true",
        help="Use provider_name column instead of split last/first",
    )
    args = parser.parse_args()

    code = args.state_code.upper()
    path = CONVERT_DIR / f"{args.module_name}.py"
    if path.exists():
        raise SystemExit(f"Already exists: {path}")

    entity_flag = "True" if args.entity_column else "False"
    multi_flag = "True" if args.multi_given_first else "False"

    if args.combined_name:
        name_block = textwrap.indent(
            """
            names = resolve_name_fields(
                provider_name=row.get("provider_name"),
                provider_type=row.get("provider_type"),
            )
            """.strip(),
            " " * 8,
        )
        load_hint = "# TODO: map raw columns; ensure provider_name + provider_type exist"
    else:
        name_block = textwrap.indent(
            f"""
            names = resolve_name_fields(
                last_name=row.get("last_name"),
                first_name=row.get("first_name"),
                mid_name=row.get("middle_name"),
                business_name=row.get("business_name"),
                provider_type=row.get("provider_type"),
                last_name_is_entity_column={entity_flag},
                split_multi_given_first_names={multi_flag},
            )
            """.strip(),
            " " * 8,
        )
        load_hint = "# TODO: map raw Excel/PDF columns in load_raw()"

    content = f'''"""Convert and clean {code} exclusion list."""

from __future__ import annotations

import pandas as pd

from src.clean.common import build_oig_record, is_empty_row, resolve_name_fields
from src.config import RAW_DIR
from src.convert.base import dedupe_records, save_cleaned, save_processed

SOURCE_STATE = "{code}"
RAW_FILE = RAW_DIR / "{args.raw_filename}"


def load_raw() -> pd.DataFrame:
    {load_hint}
    df = pd.read_excel(RAW_FILE)
    return df.dropna(how="all")


def to_oig_records(df: pd.DataFrame) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
{name_block}
        if is_empty_row(names, ["lastname", "firstname", "busname"]):
            continue
        records.append(
            build_oig_record(
                source_state=SOURCE_STATE,
                lastname=names["lastname"],
                firstname=names["firstname"],
                midname=names["midname"],
                busname=names["busname"],
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
    print(f"{code}: {{len(raw_df)}} processed, {{len(cleaned)}} cleaned records")
'''
    path.write_text(content, encoding="utf-8")
    print(f"Wrote {path.relative_to(ROOT)}")
    print()
    print("Manual registration checklist:")
    print(f"  1. data/raw/{args.raw_filename}  + update data/raw/README.md")
    print(f"  2. src/convert/run_all.py  → add src.convert.{args.module_name}")
    print(f"  3. src/config.py  → add to ALL_SOURCE_STATES")
    print("  4. sql/01_create_stage_tables.sql  → stage_* table")
    print("  5. src/load/load_to_postgres.py  → STATE_STAGE_MAP")
    print("  6. sql/03_merge_to_main.sql  → source_state IN (...)")
    print("  7. src/validate/check_import.py  → STATE_EXPECTATIONS")
    print("  8. web/exclusions/queries.py  → STATE_NAMES")
    print("  9. docs/FIELD_SEMANTICS.md + docs/STATE_MAPPING.md")
    print(" 10. bash scripts/import_local.sh --states-only")
    print()
    print("Name rules: docs/NAME_HANDLING.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

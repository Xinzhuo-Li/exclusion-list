"""End-to-end pipeline: convert, validate, load, merge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.convert.run_all import run_all as convert_all
from src.load.load_to_postgres import run as load_postgres
from src.validate.check_import import run as validate_import


def merge_to_main() -> None:
    from src.load.load_to_postgres import ROOT_DIR, get_connection

    sql_path = ROOT_DIR / "sql" / "03_merge_to_main.sql"
    with get_connection() as conn, sql_path.open(encoding="utf-8") as handle:
        with conn.cursor() as cur:
            cur.execute(handle.read())
        conn.commit()
    print("Merged cleaned_staging into exclusion_main.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run exclusion list ETL pipeline.")
    parser.add_argument(
        "--skip-nebraska",
        action="store_true",
        help="Skip Nebraska PDF conversion.",
    )
    parser.add_argument(
        "--skip-db",
        action="store_true",
        help="Skip PostgreSQL load and merge steps.",
    )
    parser.add_argument(
        "--skip-merge",
        action="store_true",
        help="Skip merge into exclusion_main.",
    )
    args = parser.parse_args()

    print("Step 1-2: Convert and clean state files...")
    convert_all(skip_nebraska=args.skip_nebraska)

    print("Step 4: Validate processed and cleaned outputs...")
    reports = validate_import()
    if not all(report["passed"] for report in reports):
        failed = [report["state"] for report in reports if not report["passed"]]
        raise SystemExit(f"Validation failed for: {', '.join(failed)}")

    if args.skip_db:
        print("Database steps skipped.")
        return

    print("Step 3: Load stage and cleaned tables into PostgreSQL...")
    load_postgres()

    if args.skip_merge:
        print("Merge step skipped.")
        return

    print("Step 5: Merge into exclusion_main...")
    merge_to_main()
    print("Pipeline complete.")


if __name__ == "__main__":
    main()

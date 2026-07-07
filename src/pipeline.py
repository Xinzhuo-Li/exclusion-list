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
from src.validate.name_audit import run as name_audit
from src.validate.quality_audit import run as quality_audit
from src.validate.run_manifest import write_run_manifest

SYNC_COLUMNS = """
    lastname, firstname, midname, busname, general, specialty,
    upin, npi, dob, address, city, state, zip_code,
    excltype, excldate, reindate, waiverdate, waiverstate,
    list_source, source_state
""".strip()


def check_runtime_dependencies(*, skip_nebraska: bool = False) -> None:
    """Fail fast with install hints before convert (TX .xls needs xlrd)."""
    from src.config import RAW_DIR

    missing: list[str] = []
    if (RAW_DIR / "Texas.xls").exists():
        try:
            import xlrd  # noqa: F401
        except ImportError:
            missing.append('xlrd>=2.0.1 (Texas.xls) — pip install -r requirements.txt')
    pdf_states = ["Wyoming.pdf", "Nebraska.pdf", "Hawaii.pdf", "Idaho.pdf", "Maine.pdf"]
    if not skip_nebraska and any((RAW_DIR / name).exists() for name in pdf_states):
        try:
            import pdfplumber  # noqa: F401
        except ImportError:
            missing.append("pdfplumber (PDF states) — pip install -r requirements.txt")
    if missing:
        raise SystemExit("Missing pipeline dependencies:\n  " + "\n  ".join(missing))


def merge_to_main() -> None:
    from src.load.load_to_postgres import ROOT_DIR, get_connection
    from src.load.merge_guard import validate_staging_before_merge

    with get_connection() as conn:
        counts = validate_staging_before_merge(conn)
        print(
            f"Pre-merge staging check OK: {len(counts)} sources, "
            f"{sum(counts.values())} total rows"
        )

    sql_path = ROOT_DIR / "sql" / "03_merge_to_main.sql"
    with get_connection() as conn, sql_path.open(encoding="utf-8") as handle:
        with conn.cursor() as cur:
            cur.execute(handle.read())
        conn.commit()
    print("Merged cleaned_staging into exclusion_main.")


def verify_main_sync() -> None:
    from src.load.load_to_postgres import get_connection

    staging_minus_sql = f"""
        SELECT COUNT(*) FROM (
            SELECT {SYNC_COLUMNS}
            FROM cleaned_staging
            EXCEPT
            SELECT {SYNC_COLUMNS}
            FROM exclusion_main
        ) diff
    """
    main_minus_sql = f"""
        SELECT COUNT(*) FROM (
            SELECT {SYNC_COLUMNS}
            FROM exclusion_main
            EXCEPT
            SELECT {SYNC_COLUMNS}
            FROM cleaned_staging
        ) diff
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM cleaned_staging")
        staging_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM exclusion_main")
        main_count = cur.fetchone()[0]
        cur.execute(staging_minus_sql)
        staging_minus_main = cur.fetchone()[0]
        cur.execute(main_minus_sql)
        main_minus_staging = cur.fetchone()[0]

    print(
        f"Sync check: staging={staging_count}, main={main_count}, "
        f"staging_minus_main={staging_minus_main}, main_minus_staging={main_minus_staging}"
    )
    if staging_count != main_count:
        raise SystemExit(
            f"exclusion_main row count ({main_count}) != cleaned_staging ({staging_count})"
        )
    if staging_minus_main or main_minus_staging:
        raise SystemExit(
            "exclusion_main is not strictly synced with cleaned_staging "
            f"(staging_minus_main={staging_minus_main}, main_minus_staging={main_minus_staging})"
        )
    print("Sync verification passed.")


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
    parser.add_argument(
        "--states-only",
        action="store_true",
        help="Skip federal LEIE convert even if data/raw/LEIE.csv exists.",
    )
    args = parser.parse_args()

    check_runtime_dependencies(skip_nebraska=args.skip_nebraska)

    print("Step 0: Record source file manifest...")
    write_run_manifest(skip_nebraska=args.skip_nebraska)

    print("Step 1: Convert and clean state files...")
    convert_all(skip_nebraska=args.skip_nebraska, skip_federal=args.states_only)

    print("Step 2: Validate processed and cleaned outputs...")
    reports = validate_import()
    if not all(report["passed"] for report in reports):
        failed = [report["state"] for report in reports if not report["passed"]]
        raise SystemExit(f"Validation failed for: {', '.join(failed)}")

    print("Step 3: Name field audit (spot-check flags)...")
    name_audit()

    print("Step 4: Quality audit (rerun consistency)...")
    audit = quality_audit()
    if not audit["summary"]["all_reruns_consistent"]:
        inconsistent = [
            item["state"]
            for item in audit["rerun_consistency"]
            if not item["consistent"]
        ]
        raise SystemExit(f"Quality audit failed for: {', '.join(inconsistent)}")

    if args.skip_db:
        print("Database steps skipped.")
        return

    print("Step 5: Load stage and cleaned tables into PostgreSQL...")
    load_postgres()

    if args.skip_merge:
        print("Merge step skipped.")
        return

    print("Step 6: Merge into exclusion_main...")
    merge_to_main()
    verify_main_sync()
    print("Pipeline complete.")


if __name__ == "__main__":
    main()

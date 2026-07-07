#!/usr/bin/env python3
"""Inventory local cleaned CSVs and optional remote exclusion_main counts."""

from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import CLEANED_DIR, CLEANED_STATE_CODES, FEDERAL_CLEANED_FILE, artifact_run_dir

RAW_DIR = ROOT / "data" / "raw"


def count_csv(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as fh:
        return sum(1 for _ in csv.reader(fh)) - 1


def local_inventory() -> dict:
    cleaned = {}
    state_total = 0
    for code in CLEANED_STATE_CODES:
        path = CLEANED_DIR / f"{code}_oig.csv"
        if not path.exists():
            continue
        rows = count_csv(path)
        cleaned[code.upper()] = {"file": str(path.relative_to(ROOT)), "rows": rows}
        state_total += rows

    federal_path = CLEANED_DIR / FEDERAL_CLEANED_FILE
    federal_rows = count_csv(federal_path) if federal_path.exists() else 0

    raw_files = sorted(p.name for p in RAW_DIR.iterdir() if p.is_file() and not p.name.startswith("."))
    convert_modules = sorted(
        p.stem
        for p in (ROOT / "src" / "convert").glob("*.py")
        if p.stem not in {"__init__", "run_all", "base", "common_dates", "common_names"}
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "local_cleaned": cleaned,
        "local_state_total": state_total,
        "local_federal_total": federal_rows,
        "local_grand_total": state_total + federal_rows,
        "raw_files": raw_files,
        "convert_modules": convert_modules,
    }


def remote_inventory() -> dict | None:
    try:
        import psycopg2
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
        conn = psycopg2.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=os.environ.get("PGPORT", "5432"),
            dbname=os.environ.get("PGDATABASE", "exclusion_list"),
            user=os.environ.get("PGUSER", "aiden"),
            password=os.environ.get("PGPASSWORD", ""),
            connect_timeout=5,
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT source_state, COUNT(*) FROM exclusion_main "
            "GROUP BY source_state ORDER BY source_state"
        )
        by_state = {row[0]: row[1] for row in cur.fetchall()}
        cur.execute("SELECT COUNT(*) FROM exclusion_main")
        total = cur.fetchone()[0]
        conn.close()
        return {"by_state": by_state, "total": total}
    except Exception as exc:
        return {"error": str(exc)}


def main() -> int:
    report = local_inventory()
    report["remote_exclusion_main"] = remote_inventory()
    out = artifact_run_dir() / f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nWrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Audit cleaned name fields; flags rows for spot-check without blocking the pipeline."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from src.clean.common import name_field_flags
from src.config import CLEANED_DIR, CLEANED_STATE_CODES, FEDERAL_CLEANED_FILE, artifact_run_dir


def _read_cleaned(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def audit_state(state_code: str) -> dict:
    path = CLEANED_DIR / f"{state_code}_oig.csv"
    rows = _read_cleaned(path)
    flagged: list[dict] = []
    flag_counts: Counter[str] = Counter()

    for index, row in enumerate(rows, start=2):
        flags = name_field_flags(row)
        if not flags:
            continue
        flag_counts.update(flags)
        flagged.append(
            {
                "csv_line": index,
                "flags": flags,
                "lastname": row.get("lastname", ""),
                "firstname": row.get("firstname", ""),
                "midname": row.get("midname", ""),
                "busname": row.get("busname", ""),
                "general": row.get("general", ""),
                "npi": row.get("npi", ""),
            }
        )

    return {
        "state": state_code.upper(),
        "total_rows": len(rows),
        "flagged_rows": len(flagged),
        "flag_counts": dict(sorted(flag_counts.items())),
        "samples": flagged[:25],
    }


def run(*, include_federal: bool = False) -> dict:
    reports = [audit_state(state) for state in CLEANED_STATE_CODES]
    if include_federal:
        federal_path = CLEANED_DIR / FEDERAL_CLEANED_FILE
        rows = _read_cleaned(federal_path)
        flagged = []
        flag_counts: Counter[str] = Counter()
        for index, row in enumerate(rows, start=2):
            flags = name_field_flags(row)
            if not flags:
                continue
            flag_counts.update(flags)
            flagged.append({"csv_line": index, "flags": flags, **{k: row.get(k, "") for k in (
                "lastname", "firstname", "midname", "busname", "general", "npi"
            )}})
        reports.append({
            "state": "OIG",
            "total_rows": len(rows),
            "flagged_rows": len(flagged),
            "flag_counts": dict(sorted(flag_counts.items())),
            "samples": flagged[:25],
        })

    total_flagged = sum(r["flagged_rows"] for r in reports)
    payload = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "states_audited": len(reports),
            "total_flagged_rows": total_flagged,
        "by_flag": dict(
            sorted(
                Counter(
                    flag
                    for report in reports
                    for flag, count in report.get("flag_counts", {}).items()
                    for _ in range(count)
                ).items()
            )
        ),
        },
        "states": reports,
    }

    run_dir = artifact_run_dir()
    out = run_dir / f"name_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with out.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    print(f"Name audit: {total_flagged} flagged row(s) across {len(reports)} source(s)")
    for report in reports:
        if report["flagged_rows"]:
            print(
                f"  {report['state']}: {report['flagged_rows']}/{report['total_rows']} flagged "
                f"({report['flag_counts']})"
            )
    print(f"Name audit report written to {out}")
    return payload


if __name__ == "__main__":
    run()

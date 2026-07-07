"""Validate processed/cleaned data and PostgreSQL imports."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path

from src.config import (
    CLEANED_DIR,
    CLEANED_STATE_CODES,
    FEDERAL_CLEANED_FILE,
    OIG_COLUMNS,
    OIG_FIELD_LENGTHS,
    PROCESSED_DIR,
    artifact_run_dir,
)

DATE_RE = re.compile(r"^\d{8}$")
NPI_RE = re.compile(r"^\d{10}$")

# Baseline counts from docs/DATA_INVENTORY.md; tolerance catches silent source drift.
STATE_EXPECTATIONS = {
    "md": {
        "processed_expected": 1605,
        "processed_tolerance": 5,
        "cleaned_expected": 1603,
        "cleaned_tolerance": 5,
        "npi_rate": 0.15,
        "excldate_rate": 0.95,
    },
    "ma": {
        "processed_expected": 294,
        "processed_tolerance": 5,
        "cleaned_expected": 294,
        "cleaned_tolerance": 5,
        "npi_rate": 0.75,
        "excldate_rate": 0.95,
    },
    "mi": {
        "processed_expected": 3982,
        "processed_tolerance": 5,
        "cleaned_expected": 4921,
        "cleaned_tolerance": 5,
        "npi_rate": 0.25,
        "excldate_rate": 0.99,
    },
    "ms": {
        "processed_expected": 194,
        "processed_tolerance": 5,
        "cleaned_expected": 193,
        "cleaned_tolerance": 5,
        "npi_rate": 0.70,
        "excldate_rate": 0.95,
    },
    "mt": {
        "processed_expected": 174,
        "processed_tolerance": 5,
        "cleaned_expected": 174,
        "cleaned_tolerance": 5,
        "npi_rate": 0.20,
        "excldate_rate": 0.95,
    },
    "ne": {
        "processed_expected": 1391,
        "processed_tolerance": 5,
        "cleaned_expected": 1390,
        "cleaned_tolerance": 5,
        "npi_rate": 0.15,
        "excldate_rate": 0.95,
    },
    "nc": {
        "processed_expected": 176,
        "processed_tolerance": 10,
        "cleaned_expected": 166,
        "cleaned_tolerance": 10,
        "npi_rate": 0.10,
        "excldate_rate": 0.90,
    },
    "nd": {
        "processed_expected": 195,
        "processed_tolerance": 10,
        "cleaned_expected": 195,
        "cleaned_tolerance": 10,
        "npi_rate": 0.10,
        "excldate_rate": 0.90,
    },
    "oh": {
        "processed_expected": 2017,
        "processed_tolerance": 15,
        "cleaned_expected": 2017,
        "cleaned_tolerance": 15,
        "npi_rate": 0.20,
        "excldate_rate": 0.90,
    },
    "nj": {
        "processed_expected": 4022,
        "processed_tolerance": 20,
        "cleaned_expected": 4021,
        "cleaned_tolerance": 20,
        "npi_rate": 0.28,
        "excldate_rate": 0.90,
    },
    "ny": {
        "processed_expected": 8931,
        "processed_tolerance": 25,
        "cleaned_expected": 8913,
        "cleaned_tolerance": 25,
        "npi_rate": 0.24,
        "excldate_rate": 0.95,
    },
    "pa": {
        "processed_expected": 6659,
        "processed_tolerance": 25,
        "cleaned_expected": 6591,
        "cleaned_tolerance": 25,
        "npi_rate": 0.22,
        "excldate_rate": 0.95,
    },
    "ca": {
        "processed_expected": 23120,
        "processed_tolerance": 50,
        "cleaned_expected": 23094,
        "cleaned_tolerance": 50,
        "npi_rate": 0.12,
        "excldate_rate": 0.95,
    },
    "ga": {
        "processed_expected": 1370,
        "processed_tolerance": 10,
        "cleaned_expected": 1346,
        "cleaned_tolerance": 15,
        "npi_rate": 0.02,
        "excldate_rate": 0.0,
    },
    "hi": {
        "processed_expected": 213,
        "processed_tolerance": 5,
        "cleaned_expected": 213,
        "cleaned_tolerance": 5,
        "npi_rate": 0.0,
        "excldate_rate": 0.90,
    },
    "id": {
        "processed_expected": 171,
        "processed_tolerance": 5,
        "cleaned_expected": 171,
        "cleaned_tolerance": 5,
        "npi_rate": 0.0,
        "excldate_rate": 0.90,
    },
    "il": {
        "processed_expected": 3229,
        "processed_tolerance": 15,
        "cleaned_expected": 3203,
        "cleaned_tolerance": 15,
        "npi_rate": 0.20,
        "excldate_rate": 0.95,
    },
    "in": {
        "processed_expected": 151,
        "processed_tolerance": 5,
        "cleaned_expected": 151,
        "cleaned_tolerance": 5,
        "npi_rate": 0.50,
        "excldate_rate": 0.95,
    },
    "ia": {
        "processed_expected": 1272,
        "processed_tolerance": 10,
        "cleaned_expected": 1271,
        "cleaned_tolerance": 10,
        "npi_rate": 0.30,
        "excldate_rate": 0.95,
    },
    "ks": {
        "processed_expected": 199,
        "processed_tolerance": 5,
        "cleaned_expected": 198,
        "cleaned_tolerance": 5,
        "npi_rate": 0.20,
        "excldate_rate": 0.95,
    },
    "ky": {
        "processed_expected": 397,
        "processed_tolerance": 10,
        "cleaned_expected": 396,
        "cleaned_tolerance": 10,
        "npi_rate": 0.30,
        "excldate_rate": 0.95,
    },
    "la": {
        "processed_expected": 5880,
        "processed_tolerance": 25,
        "cleaned_expected": 5859,
        "cleaned_tolerance": 25,
        "npi_rate": 0.08,
        "excldate_rate": 0.25,
    },
    "me": {
        "processed_expected": 1108,
        "processed_tolerance": 10,
        "cleaned_expected": 1108,
        "cleaned_tolerance": 10,
        "npi_rate": 0.0,
        "excldate_rate": 0.95,
    },
    "al": {
        "processed_expected": 2086,
        "processed_tolerance": 15,
        "cleaned_expected": 2086,
        "cleaned_tolerance": 15,
        "npi_rate": 0.0,
        "excldate_rate": 0.95,
    },
    "ak": {
        "processed_expected": 301,
        "processed_tolerance": 5,
        "cleaned_expected": 301,
        "cleaned_tolerance": 5,
        "npi_rate": 0.0,
        "excldate_rate": 0.95,
    },
    "az": {
        "processed_expected": 708,
        "processed_tolerance": 10,
        "cleaned_expected": 707,
        "cleaned_tolerance": 10,
        "npi_rate": 0.50,
        "excldate_rate": 0.95,
    },
    "ar": {
        "processed_expected": 2210,
        "processed_tolerance": 15,
        "cleaned_expected": 2208,
        "cleaned_tolerance": 15,
        "npi_rate": 0.0,
        "excldate_rate": 0.0,
    },
    "co": {
        "processed_expected": 318,
        "processed_tolerance": 5,
        "cleaned_expected": 316,
        "cleaned_tolerance": 5,
        "npi_rate": 0.05,
        "excldate_rate": 0.95,
    },
    "ct": {
        "processed_expected": 89,
        "processed_tolerance": 5,
        "cleaned_expected": 89,
        "cleaned_tolerance": 5,
        "npi_rate": 0.0,
        "excldate_rate": 0.95,
    },
    "de": {
        "processed_expected": 1685,
        "processed_tolerance": 15,
        "cleaned_expected": 1666,
        "cleaned_tolerance": 15,
        "npi_rate": 0.35,
        "excldate_rate": 0.90,
    },
    "dc": {
        "processed_expected": 93,
        "processed_tolerance": 5,
        "cleaned_expected": 93,
        "cleaned_tolerance": 5,
        "npi_rate": 0.10,
        "excldate_rate": 0.95,
    },
    "fl": {
        "processed_expected": 83630,
        "processed_tolerance": 100,
        "cleaned_expected": 83114,
        "cleaned_tolerance": 100,
        "npi_rate": 0.0,
        "excldate_rate": 0.95,
    },
    "sc": {
        "processed_expected": 1329,
        "processed_tolerance": 15,
        "cleaned_expected": 1329,
        "cleaned_tolerance": 15,
        "npi_rate": 0.35,
        "excldate_rate": 0.90,
    },
    "tn": {
        "processed_expected": 21,
        "processed_tolerance": 5,
        "cleaned_expected": 21,
        "cleaned_tolerance": 5,
        "npi_rate": 0.0,
        "excldate_rate": 0.90,
    },
    "tx": {
        "processed_expected": 13344,
        "processed_tolerance": 50,
        "cleaned_expected": 13324,
        "cleaned_tolerance": 50,
        "npi_rate": 0.04,
        "excldate_rate": 0.95,
    },
    "vt": {
        "processed_expected": 73,
        "processed_tolerance": 10,
        "cleaned_expected": 64,
        "cleaned_tolerance": 10,
        "npi_rate": 0.50,
        "excldate_rate": 0.90,
    },
    "wa": {
        "processed_expected": 234,
        "processed_tolerance": 10,
        "cleaned_expected": 234,
        "cleaned_tolerance": 10,
        "npi_rate": 0.70,
        "excldate_rate": 0.95,
    },
    "wv": {
        "processed_expected": 162,
        "processed_tolerance": 10,
        "cleaned_expected": 162,
        "cleaned_tolerance": 10,
        "npi_rate": 0.30,
        "excldate_rate": 0.50,
    },
    "wy": {
        "processed_expected": 108,
        "processed_tolerance": 10,
        "cleaned_expected": 108,
        "cleaned_tolerance": 10,
        "npi_rate": 0.05,
        "excldate_rate": 0.95,
    },
}

FEDERAL_EXPECTATIONS = {
    "processed_expected": 83464,
    "processed_tolerance": 100,
    "cleaned_expected": 83464,
    "cleaned_tolerance": 100,
    "npi_rate": 0.10,
    "excldate_rate": 0.95,
    "list_source": "federal",
}


def _count_within_tolerance(actual: int, expected: int, tolerance: int) -> bool:
    return abs(actual - expected) <= tolerance


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _rate(values: list[str], predicate) -> float:
    if not values:
        return 0.0
    return sum(1 for value in values if predicate(value)) / len(values)


def validate_state(state: str) -> dict:
    processed_path = PROCESSED_DIR / f"{state}_raw.csv"
    cleaned_path = CLEANED_DIR / f"{state}_oig.csv"
    processed_rows = _read_csv(processed_path)
    cleaned_rows = _read_csv(cleaned_path)
    expectations = STATE_EXPECTATIONS[state]

    npi_values = [row.get("npi", "") for row in cleaned_rows]
    excldate_values = [row.get("excldate", "") for row in cleaned_rows]
    length_violations = []
    for row in cleaned_rows:
        for field in ("npi", "excldate", "reindate", "dob", "state", "zip_code"):
            value = row.get(field, "")
            max_len = OIG_FIELD_LENGTHS.get(field)
            if max_len and value and len(value) > max_len:
                length_violations.append({"field": field, "value": value, "length": len(value)})

    report = {
        "state": state.upper(),
        "processed_rows": len(processed_rows),
        "cleaned_rows": len(cleaned_rows),
        "npi_valid_rate": _rate(npi_values, lambda v: bool(v) and bool(NPI_RE.match(v))),
        "excldate_valid_rate": _rate(
            excldate_values, lambda v: (not v) or bool(DATE_RE.match(v))
        ),
        "length_violations": length_violations[:10],
        "sample_records": cleaned_rows[:3],
        "checks": {
            "processed_count_ok": _count_within_tolerance(
                len(processed_rows),
                expectations["processed_expected"],
                expectations["processed_tolerance"],
            ),
            "cleaned_count_ok": _count_within_tolerance(
                len(cleaned_rows),
                expectations["cleaned_expected"],
                expectations["cleaned_tolerance"],
            ),
            "npi_rate_ok": _rate(npi_values, lambda v: bool(v))
            >= expectations["npi_rate"],
            "excldate_rate_ok": _rate(excldate_values, lambda v: bool(v))
            >= expectations["excldate_rate"],
            "date_format_ok": _rate(excldate_values, lambda v: (not v) or bool(DATE_RE.match(v)))
            >= 0.99,
            "field_length_ok": len(length_violations) == 0,
        },
    }
    report["passed"] = all(report["checks"].values())
    return report


def validate_federal() -> dict:
    processed_path = PROCESSED_DIR / "federal_raw.csv"
    cleaned_path = CLEANED_DIR / FEDERAL_CLEANED_FILE
    processed_rows = _read_csv(processed_path)
    cleaned_rows = _read_csv(cleaned_path)
    expectations = FEDERAL_EXPECTATIONS

    npi_values = [row.get("npi", "") for row in cleaned_rows]
    excldate_values = [row.get("excldate", "") for row in cleaned_rows]
    list_source_ok = all(row.get("list_source") == "federal" for row in cleaned_rows)
    source_state_ok = all(row.get("source_state") == "OIG" for row in cleaned_rows)

    report = {
        "state": "OIG",
        "processed_rows": len(processed_rows),
        "cleaned_rows": len(cleaned_rows),
        "npi_valid_rate": _rate(npi_values, lambda v: bool(v) and bool(NPI_RE.match(v))),
        "excldate_valid_rate": _rate(
            excldate_values, lambda v: (not v) or bool(DATE_RE.match(v))
        ),
        "length_violations": [],
        "sample_records": cleaned_rows[:3],
        "checks": {
            "processed_count_ok": _count_within_tolerance(
                len(processed_rows),
                expectations["processed_expected"],
                expectations["processed_tolerance"],
            ),
            "cleaned_count_ok": _count_within_tolerance(
                len(cleaned_rows),
                expectations["cleaned_expected"],
                expectations["cleaned_tolerance"],
            ),
            "npi_rate_ok": _rate(npi_values, lambda v: bool(v)) >= expectations["npi_rate"],
            "excldate_rate_ok": _rate(excldate_values, lambda v: bool(v))
            >= expectations["excldate_rate"],
            "date_format_ok": _rate(excldate_values, lambda v: (not v) or bool(DATE_RE.match(v)))
            >= 0.99,
            "field_length_ok": True,
            "list_source_ok": list_source_ok,
            "source_state_ok": source_state_ok,
        },
    }
    report["passed"] = all(report["checks"].values())
    return report


def write_reports(reports: list[dict]) -> Path:
    run_dir = artifact_run_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = run_dir / f"validation_report_{timestamp}.json"
    with output.open("w", encoding="utf-8") as handle:
        json.dump(reports, handle, indent=2)
    return output


def run(states: list[str] | None = None) -> list[dict]:
    selected = states or CLEANED_STATE_CODES
    reports = [validate_state(state) for state in selected]
    if (CLEANED_DIR / FEDERAL_CLEANED_FILE).exists():
        reports.append(validate_federal())
    output = write_reports(reports)
    for report in reports:
        status = "PASS" if report["passed"] else "FAIL"
        print(
            f"{report['state']}: {status} "
            f"(processed={report['processed_rows']}, cleaned={report['cleaned_rows']})"
        )
    print(f"Validation report written to {output}")
    return reports


if __name__ == "__main__":
    run()

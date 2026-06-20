"""Validate processed/cleaned data and PostgreSQL imports."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path

from src.config import CLEANED_DIR, DOCS_DIR, OIG_COLUMNS, OIG_FIELD_LENGTHS, PROCESSED_DIR

DATE_RE = re.compile(r"^\d{8}$")
NPI_RE = re.compile(r"^\d{10}$")

STATE_EXPECTATIONS = {
    "md": {"processed_min": 1500, "cleaned_min": 1500, "npi_rate": 0.15, "excldate_rate": 0.95},
    "ma": {"processed_min": 250, "cleaned_min": 250, "npi_rate": 0.75, "excldate_rate": 0.95},
    "mi": {"processed_min": 3500, "cleaned_min": 4800, "npi_rate": 0.25, "excldate_rate": 0.99},
    "ms": {"processed_min": 180, "cleaned_min": 180, "npi_rate": 0.70, "excldate_rate": 0.95},
    "mt": {"processed_min": 150, "cleaned_min": 150, "npi_rate": 0.20, "excldate_rate": 0.95},
    "ne": {"processed_min": 500, "cleaned_min": 500, "npi_rate": 0.15, "excldate_rate": 0.95},
}


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
            "processed_count_ok": len(processed_rows) >= expectations["processed_min"],
            "cleaned_count_ok": len(cleaned_rows) >= expectations["cleaned_min"],
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


def write_reports(reports: list[dict]) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = DOCS_DIR / f"validation_report_{timestamp}.json"
    with output.open("w", encoding="utf-8") as handle:
        json.dump(reports, handle, indent=2)
    return output


def run(states: list[str] | None = None) -> list[dict]:
    selected = states or list(STATE_EXPECTATIONS.keys())
    reports = [validate_state(state) for state in selected]
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

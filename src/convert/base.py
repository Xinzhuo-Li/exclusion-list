"""Shared helpers for state conversion pipelines."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.config import CLEANED_DIR, DOCS_DIR, OIG_COLUMNS, PROCESSED_DIR

# Identity fields used to decide whether two records are true duplicates.
DEDUP_IDENTITY_FIELDS = [
    "source_state",
    "lastname",
    "firstname",
    "midname",
    "busname",
    "npi",
    "dob",
    "address",
    "city",
    "state",
    "zip_code",
    "general",
    "specialty",
    "excltype",
    "excldate",
    "reindate",
]


def ensure_output_dirs() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)


def save_processed(df: pd.DataFrame, state_code: str) -> Path:
    ensure_output_dirs()
    path = PROCESSED_DIR / f"{state_code.lower()}_raw.csv"
    df.to_csv(path, index=False)
    return path


def save_cleaned(records: Iterable[dict[str, str]], state_code: str) -> Path:
    ensure_output_dirs()
    path = CLEANED_DIR / f"{state_code.lower()}_oig.csv"
    fieldnames = OIG_COLUMNS + ["source_state"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({key: record.get(key, "") for key in fieldnames})
    return path


def record_identity_key(record: dict[str, str]) -> tuple[str, ...]:
    """Build a dedup key from all identity fields.

    Two records are considered duplicates only when every identity field matches.
    This avoids collapsing different individuals who share a last name, date, or NPI.
    """
    return tuple(record.get(field, "") or "" for field in DEDUP_IDENTITY_FIELDS)


def dedupe_records(
    records: list[dict[str, str]],
    *,
    state_code: str = "",
    log_dropped: bool = True,
) -> list[dict[str, str]]:
    seen: set[tuple[str, ...]] = set()
    deduped: list[dict[str, str]] = []
    dropped: list[dict[str, str]] = []

    for record in records:
        key = record_identity_key(record)
        if key in seen:
            dropped.append(record)
            continue
        seen.add(key)
        deduped.append(record)

    if log_dropped and dropped and state_code:
        _write_dedup_log(state_code, dropped)

    return deduped


def _write_dedup_log(state_code: str, dropped: list[dict[str, str]]) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = DOCS_DIR / f"dedup_dropped_{state_code.lower()}.json"
    payload = {
        "state": state_code.upper(),
        "dropped_count": len(dropped),
        "generated_at": datetime.now().isoformat(),
        "reason": "Exact duplicate: all identity fields identical to a prior record.",
        "identity_fields": DEDUP_IDENTITY_FIELDS,
        "dropped_records": dropped,
    }
    with log_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def save_cleaned_with_dedup(
    records: list[dict[str, str]],
    state_code: str,
) -> tuple[Path, list[dict[str, str]]]:
    deduped = dedupe_records(records, state_code=state_code)
    path = save_cleaned(deduped, state_code)
    return path, deduped

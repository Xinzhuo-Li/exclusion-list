"""Regression tests for cleaned record counts (aligned with DATA_INVENTORY)."""

from __future__ import annotations

import csv

import pytest

from src.config import CLEANED_DIR, PROCESSED_DIR
from src.validate.check_import import STATE_EXPECTATIONS

# Baseline aligned with STATE_EXPECTATIONS after Le Luo merge (2026-07).
BASELINE = {state: {
    "processed": STATE_EXPECTATIONS[state]["processed_expected"],
    "cleaned": STATE_EXPECTATIONS[state]["cleaned_expected"],
} for state in STATE_EXPECTATIONS}


def _count_csv_rows(path) -> int:
    if not path.exists():
        return -1
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


@pytest.mark.parametrize("state", list(BASELINE.keys()))
def test_processed_row_count_within_tolerance(state: str) -> None:
    path = PROCESSED_DIR / f"{state}_raw.csv"
    if not path.exists():
        pytest.skip(f"Missing {path}")
    count = _count_csv_rows(path)
    expected = BASELINE[state]["processed"]
    tolerance = STATE_EXPECTATIONS[state]["processed_tolerance"]
    assert abs(count - expected) <= tolerance, (
        f"{state.upper()} processed={count}, expected {expected} ±{tolerance}"
    )


@pytest.mark.parametrize("state", list(BASELINE.keys()))
def test_cleaned_row_count_within_tolerance(state: str) -> None:
    path = CLEANED_DIR / f"{state}_oig.csv"
    if not path.exists():
        pytest.skip(f"Missing {path}")
    count = _count_csv_rows(path)
    expected = BASELINE[state]["cleaned"]
    tolerance = STATE_EXPECTATIONS[state]["cleaned_tolerance"]
    assert abs(count - expected) <= tolerance, (
        f"{state.upper()} cleaned={count}, expected {expected} ±{tolerance}"
    )

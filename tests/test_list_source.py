"""Tests for list_source column in cleaned output."""

from __future__ import annotations

import csv

import pytest

from src.config import (
    CLEANED_DIR,
    CLEANED_STATE_CODES,
    FEDERAL_CLEANED_FILE,
    LIST_SOURCE_FEDERAL,
    LIST_SOURCE_STATE,
)


def _read_cleaned(state: str) -> list[dict[str, str]]:
    path = CLEANED_DIR / f"{state}_oig.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@pytest.mark.parametrize("state", CLEANED_STATE_CODES)
def test_cleaned_csv_has_list_source_column(state: str) -> None:
    rows = _read_cleaned(state)
    if not rows:
        pytest.skip(f"Missing {state}_oig.csv")
    assert "list_source" in rows[0]


@pytest.mark.parametrize("state", CLEANED_STATE_CODES)
def test_all_rows_list_source_is_state(state: str) -> None:
    rows = _read_cleaned(state)
    if not rows:
        pytest.skip(f"Missing {state}_oig.csv")
    bad = [r for r in rows if r.get("list_source") != LIST_SOURCE_STATE]
    assert not bad, f"{state}: {len(bad)} rows with unexpected list_source"


def test_federal_leie_list_source() -> None:
    path = CLEANED_DIR / FEDERAL_CLEANED_FILE
    if not path.exists():
        pytest.skip("federal_oig.csv not built")
    rows = list(csv.DictReader(path.open()))
    assert len(rows) > 80000
    assert all(r.get("list_source") == LIST_SOURCE_FEDERAL for r in rows)
    assert all(r.get("source_state") == "OIG" for r in rows)

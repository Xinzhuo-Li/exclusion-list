"""Tests for Pennsylvania CAO state parsing and reindate rules."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.config import CLEANED_DIR
from src.convert.pennsylvania import pa_reindate_for_status, parse_pa_cao_state


@pytest.mark.parametrize(
    "cao,expected",
    [
        ("Cumberland", "PA"),
        ("Philadelphia", "PA"),
        ("Out of State (NJ)", "NJ"),
        ("Out of State (NY)", "NY"),
        ("Out-of-State (FL)", "FL"),
        ("Out of State", ""),
        ("", "PA"),
    ],
)
def test_parse_pa_cao_state(cao: str, expected: str) -> None:
    assert parse_pa_cao_state(cao) == expected


def test_pa_reindate_only_for_reinstated() -> None:
    assert pa_reindate_for_status("Reinstated", "20200101") == "20200101"
    assert pa_reindate_for_status("Precluded", "20200101") == ""
    assert pa_reindate_for_status("Terminated", "6/12/2025") == ""


def test_pa_cleaned_reindate_rules() -> None:
    path = CLEANED_DIR / "pa_oig.csv"
    if not path.exists():
        pytest.skip("Run PA convert first")
    rows = list(csv.DictReader(path.open()))
    rein = [r for r in rows if (r.get("excltype") or "").upper() == "REINSTATED"]
    non_rein_with_reindate = [
        r
        for r in rows
        if (r.get("excltype") or "").upper() != "REINSTATED" and (r.get("reindate") or "").strip()
    ]
    assert rein, "expected Reinstated rows in PA cleaned data"
    assert all((r.get("reindate") or "").strip() for r in rein)
    assert not non_rein_with_reindate, "non-Reinstated PA rows must not have reindate"


def test_pa_out_of_state_not_default_pa() -> None:
    path = CLEANED_DIR / "pa_oig.csv"
    if not path.exists():
        pytest.skip("Run PA convert first")
    rows = list(csv.DictReader(path.open()))
    # Rows with non-PA address state should exist after CAO parse
    non_pa = [r for r in rows if (r.get("state") or "").strip() and r["state"] != "PA"]
    assert len(non_pa) >= 500

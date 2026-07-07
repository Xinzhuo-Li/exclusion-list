"""Tests for Mississippi indefinite REINDATE handling."""

from __future__ import annotations

import pytest

from src.clean.common import normalize_reindate
from src.config import INDEFINITE_DATE_SERIAL


@pytest.mark.parametrize(
    ("end_date", "exclusion_period", "expected"),
    [
        (INDEFINITE_DATE_SERIAL, "", ""),
        ("401768", "", ""),
        ("", "2020-01-01 - Indefinite", ""),
        ("", "Indefinite", ""),
        (45306, "", "20240115"),  # real end date
        ("20281119", "", "20281119"),
    ],
)
def test_normalize_reindate(end_date, exclusion_period, expected) -> None:
    assert normalize_reindate(end_date, exclusion_period) == expected

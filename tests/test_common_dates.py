"""Tests for shared date and NPI normalization."""

from __future__ import annotations

from datetime import datetime

import pytest

from src.clean.common import clean_npi, excel_serial_to_yyyymmdd
from src.config import INDEFINITE_DATE_SERIAL


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("20240115", "20240115"),
        ("2024-01-15", "20240115"),
        ("1/15/2024", "20240115"),
        (45306, "20240115"),  # Excel serial for 2024-01-15
        ("", ""),
        (None, ""),
        (INDEFINITE_DATE_SERIAL, ""),
        (401768, ""),
        (500000, ""),  # out of range sentinel
    ],
)
def test_excel_serial_to_yyyymmdd(value, expected) -> None:
    assert excel_serial_to_yyyymmdd(value) == expected


def test_excel_serial_datetime_input() -> None:
    assert excel_serial_to_yyyymmdd(datetime(2024, 6, 1)) == "20240601"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1891706537", "1891706537"),
        (1891706537.0, "1891706537"),
        ("189170653", ""),
        ("", ""),
        (None, ""),
        ("N/A", ""),
    ],
)
def test_clean_npi(value, expected) -> None:
    assert clean_npi(value) == expected

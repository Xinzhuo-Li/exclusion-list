"""Tests for Michigan multi-date sanction parsing."""

from __future__ import annotations

from datetime import datetime

import pytest

from src.convert.michigan_dates import parse_michigan_date_field


def test_single_date_token() -> None:
    assert parse_michigan_date_field("3/15/2020") == ["20200315"]


def test_multiple_date_tokens() -> None:
    result = parse_michigan_date_field("3/15/2020 6/1/2021")
    assert result == ["20200315", "20210601"]


def test_datetime_input() -> None:
    assert parse_michigan_date_field(datetime(2020, 3, 15)) == ["20200315"]


def test_empty_value() -> None:
    assert parse_michigan_date_field("") == []
    assert parse_michigan_date_field(None) == []


def test_excel_serial_fallback() -> None:
    # 45306 = 2024-01-15
    assert parse_michigan_date_field(45306) == ["20240115"]

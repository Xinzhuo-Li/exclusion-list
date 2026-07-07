"""Tests for Ohio status → excltype mapping."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.config import CLEANED_DIR


def test_ohio_excltype_from_status_allows_empty() -> None:
    path = CLEANED_DIR / "oh_oig.csv"
    if not path.exists():
        pytest.skip("Run OH convert first")
    rows = list(csv.DictReader(path.open()))
    assert len(rows) == 2017
    empty_excltype = [r for r in rows if not (r.get("excltype") or "").strip()]
    assert len(empty_excltype) == 1
    assert empty_excltype[0]["lastname"] == "Nelson-Lyles"
    assert empty_excltype[0]["firstname"] == "Alberta"

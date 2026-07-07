"""Partial load policy for load_to_postgres."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.load.load_to_postgres import load_cleaned_data
from src.load.merge_guard import PartialLoadError


def test_load_cleaned_data_rejects_partial_without_env(monkeypatch):
    monkeypatch.delenv("ALLOW_PARTIAL_LOAD", raising=False)
    conn = MagicMock()
    with pytest.raises(PartialLoadError):
        load_cleaned_data(conn, states=["tx"])


def test_load_cleaned_data_allows_partial_with_env(monkeypatch):
    monkeypatch.setenv("ALLOW_PARTIAL_LOAD", "1")
    conn = MagicMock()

    def fake_truediv(_self, name: str) -> MagicMock:
        path = MagicMock()
        path.exists.return_value = name == "tx_oig.csv"
        return path

    with patch("src.load.load_to_postgres.truncate_table"), patch(
        "src.load.load_to_postgres.load_csv_to_table", return_value=10
    ), patch("src.load.load_to_postgres.CLEANED_DIR") as cleaned_dir:
        cleaned_dir.__truediv__ = fake_truediv
        counts = load_cleaned_data(conn, states=["tx"])
    assert counts == {"tx": 10}

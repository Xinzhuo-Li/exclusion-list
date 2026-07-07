"""Ensure pipeline SYNC_COLUMNS match sql/04_verify_main_sync.sql EXCEPT lists."""

from __future__ import annotations

import re
from pathlib import Path

from src.pipeline import SYNC_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
VERIFY_SQL = ROOT / "sql" / "04_verify_main_sync.sql"


def _columns_from_sql() -> list[str]:
    text = VERIFY_SQL.read_text(encoding="utf-8")
    match = re.search(
        r"SELECT\s+(lastname.*?source_state)\s+FROM cleaned_staging",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    assert match, "Could not parse column list from 04_verify_main_sync.sql"
    return [col.strip() for col in match.group(1).split(",")]


def test_sync_columns_match_verify_sql():
    pipeline_cols = [col.strip() for col in SYNC_COLUMNS.replace("\n", " ").split(",")]
    sql_cols = _columns_from_sql()
    assert pipeline_cols == sql_cols

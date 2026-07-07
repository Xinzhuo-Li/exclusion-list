"""Tests for merge guard — partial load and staging completeness."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.config import ACTIVE_SOURCE_STATES
from src.load.merge_guard import (
    EXPECTED_SOURCE_COUNT,
    FEDERAL_SOURCE_STATE,
    PartialLoadError,
    StagingIncompleteError,
    assert_full_cleaned_load_scope,
    expected_staging_sources,
    validate_staging_before_merge,
)


def test_expected_staging_sources_count():
    sources = expected_staging_sources()
    assert len(sources) == EXPECTED_SOURCE_COUNT == 40
    assert FEDERAL_SOURCE_STATE in sources
    assert set(ACTIVE_SOURCE_STATES).issubset(sources)


def test_assert_full_cleaned_load_scope_allows_none():
    assert_full_cleaned_load_scope(None)


def test_assert_full_cleaned_load_scope_allows_full_set():
    from src.config import CLEANED_STATE_CODES

    assert_full_cleaned_load_scope(CLEANED_STATE_CODES)


def test_assert_full_cleaned_load_scope_rejects_partial(monkeypatch):
    monkeypatch.delenv("ALLOW_PARTIAL_LOAD", raising=False)
    with pytest.raises(PartialLoadError, match="Partial cleaned load refused"):
        assert_full_cleaned_load_scope(["tx"])


def test_assert_full_cleaned_load_scope_allows_partial_with_env(monkeypatch):
    monkeypatch.setenv("ALLOW_PARTIAL_LOAD", "1")
    assert_full_cleaned_load_scope(["tx"])


def _staging_rows(source_counts: dict[str, int]) -> MagicMock:
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    cursor.fetchall.return_value = list(source_counts.items())
    return conn


def test_validate_staging_before_merge_complete(monkeypatch):
    monkeypatch.setattr("src.load.merge_guard.MIN_TOTAL_ROWS", 1000)
    expected = expected_staging_sources()
    counts = {source: 100 for source in expected}
    conn = _staging_rows(counts)
    result = validate_staging_before_merge(conn)
    assert len(result) == 40
    assert sum(result.values()) == 4000


def test_validate_staging_before_merge_missing_state():
    expected = expected_staging_sources()
    counts = {source: 50 for source in expected if source != "TX"}
    conn = _staging_rows(counts)
    with pytest.raises(StagingIncompleteError, match="missing"):
        validate_staging_before_merge(conn)


def test_validate_staging_before_merge_too_few_rows():
    expected = expected_staging_sources()
    counts = {source: 1 for source in expected}
    conn = _staging_rows(counts)
    with pytest.raises(StagingIncompleteError, match="below minimum"):
        validate_staging_before_merge(conn)

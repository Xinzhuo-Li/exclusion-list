"""Guards against partial staging loads before merge into exclusion_main."""

from __future__ import annotations

import os
from typing import Any

from src.config import ACTIVE_SOURCE_STATES, CLEANED_STATE_CODES, FEDERAL_CLEANED_FILE, CLEANED_DIR

FEDERAL_SOURCE_STATE = "OIG"
EXPECTED_SOURCE_COUNT = len(ACTIVE_SOURCE_STATES) + 1  # 39 states + OIG
MIN_TOTAL_ROWS = 250_000
EXPECTED_TOTAL_ROWS = 256_776


class PartialLoadError(RuntimeError):
    """Raised when a subset of states is loaded without ALLOW_PARTIAL_LOAD."""


class StagingIncompleteError(RuntimeError):
    """Raised when cleaned_staging is missing sources required for merge."""


def expected_staging_sources() -> set[str]:
    """Uppercase source_state values that must appear in cleaned_staging before merge."""
    return set(ACTIVE_SOURCE_STATES) | {FEDERAL_SOURCE_STATE}


def assert_full_cleaned_load_scope(states: list[str] | None) -> None:
    """Refuse partial cleaned loads unless ALLOW_PARTIAL_LOAD=1 (dev only)."""
    if states is None:
        return

    requested = {code.lower() for code in states}
    full = set(CLEANED_STATE_CODES)
    if requested == full:
        return

    if os.environ.get("ALLOW_PARTIAL_LOAD") == "1":
        return

    missing = sorted(full - requested)
    raise PartialLoadError(
        f"Partial cleaned load refused ({len(requested)}/{len(full)} state files). "
        f"Missing: {', '.join(missing)}. "
        "Merge deletes all 39 state slices from exclusion_main — partial load would drop "
        "the missing states. Use full load (states=None) or set ALLOW_PARTIAL_LOAD=1 for "
        "dev-only staging experiments (never merge after partial load)."
    )


def federal_csv_expected() -> bool:
    return (CLEANED_DIR / FEDERAL_CLEANED_FILE).exists()


def validate_staging_before_merge(conn: Any) -> dict[str, int]:
    """
    Ensure cleaned_staging has all required source_state slices with rows > 0.

    Returns {source_state: row_count} for logging.
    """
    expected = expected_staging_sources()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT source_state, COUNT(*) AS cnt
            FROM cleaned_staging
            GROUP BY source_state
            """
        )
        rows = {str(source_state): int(cnt) for source_state, cnt in cur.fetchall()}

    present = set(rows)
    missing = sorted(expected - present)
    if missing:
        raise StagingIncompleteError(
            f"cleaned_staging missing {len(missing)} source(s): {', '.join(missing)}. "
            "Refusing merge — would delete these slices from exclusion_main without re-inserting."
        )

    empty = sorted(source for source, cnt in rows.items() if cnt <= 0 and source in expected)
    if empty:
        raise StagingIncompleteError(
            f"cleaned_staging has zero-row source(s): {', '.join(empty)}. Refusing merge."
        )

    extra = sorted(present - expected)
    if extra:
        raise StagingIncompleteError(
            f"cleaned_staging has unexpected source_state value(s): {', '.join(extra)}"
        )

    if federal_csv_expected() and FEDERAL_SOURCE_STATE not in present:
        raise StagingIncompleteError(
            f"{FEDERAL_CLEANED_FILE} exists but cleaned_staging has no OIG rows."
        )

    total = sum(rows.values())
    if total < MIN_TOTAL_ROWS:
        raise StagingIncompleteError(
            f"cleaned_staging total rows ({total}) below minimum ({MIN_TOTAL_ROWS}). "
            "Likely partial load — refusing merge."
        )

    return rows

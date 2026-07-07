"""Tests for name audit validation."""

from __future__ import annotations

from src.clean.common import name_field_flags
from src.validate.name_audit import audit_state


def test_name_field_flags_detects_empty() -> None:
    assert "empty_all_names" in name_field_flags(
        {"lastname": "", "firstname": "", "midname": "", "busname": ""}
    )


def test_audit_state_runs_on_existing_cleaned(tmp_path, monkeypatch) -> None:
    from src.config import CLEANED_DIR

    # Use real md file if present
    if not (CLEANED_DIR / "md_oig.csv").exists():
        return
    report = audit_state("md")
    assert report["state"] == "MD"
    assert report["total_rows"] > 0

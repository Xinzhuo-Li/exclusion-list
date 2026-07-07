"""Tests for exact-duplicate deduplication."""

from __future__ import annotations

from src.convert.base import dedupe_records, record_identity_key


def _record(**overrides) -> dict[str, str]:
    base = {
        "source_state": "MD",
        "lastname": "Smith",
        "firstname": "John",
        "midname": "",
        "busname": "",
        "npi": "1234567890",
        "dob": "",
        "address": "123 Main St",
        "city": "Baltimore",
        "state": "MD",
        "zip_code": "21201",
        "general": "Physician",
        "specialty": "",
        "excltype": "MDH",
        "excldate": "20200101",
        "reindate": "",
    }
    base.update(overrides)
    return base


def test_dedup_removes_exact_duplicate() -> None:
    records = [_record(), _record()]
    result = dedupe_records(records, state_code="", log_dropped=False)
    assert len(result) == 1


def test_dedup_keeps_different_excldate() -> None:
    records = [_record(excldate="20200101"), _record(excldate="20210101")]
    result = dedupe_records(records, state_code="", log_dropped=False)
    assert len(result) == 2


def test_dedup_keeps_same_name_different_npi() -> None:
    records = [_record(npi="1111111111"), _record(npi="2222222222")]
    result = dedupe_records(records, state_code="", log_dropped=False)
    assert len(result) == 2


def test_record_identity_key_uses_all_fields() -> None:
    r1 = _record()
    r2 = _record(reindate="20251231")
    assert record_identity_key(r1) != record_identity_key(r2)

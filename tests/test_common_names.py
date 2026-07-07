"""Tests for name parsing and organization detection."""

from __future__ import annotations

import pytest

from src.clean.common import (
    is_organization,
    looks_like_facility_name,
    name_field_flags,
    parse_alias_name,
    parse_combined_name,
    parse_last_first,
    parse_provider_name,
    resolve_name_fields,
    split_multi_given_first_name,
    truncate_field,
)


@pytest.mark.parametrize(
    ("name", "hint", "expected"),
    [
        ("Acme Home Care LLC", "", True),
        ("Smith, John", "Individual", False),
        ("Regional Hospital", "Business Entity", True),
        ("Jane Doe", "Person", False),
    ],
)
def test_is_organization(name, hint, expected) -> None:
    assert is_organization(name, hint) is expected


@pytest.mark.parametrize(
    ("name", "last", "first", "mid"),
    [
        ("Smith, John A", "Smith", "John", "A"),
        ("John Smith", "Smith", "John", ""),
        ("Mary Ann Lee", "Lee", "Mary", "Ann"),
        ("Solo", "Solo", "", ""),
    ],
)
def test_parse_last_first(name, last, first, mid) -> None:
    assert parse_last_first(name) == (last, first, mid)


def test_parse_alias_name() -> None:
    assert parse_alias_name("a.k.a. Clement, Saul") == ("Clement", "Saul", "")


def test_parse_provider_name_individual() -> None:
    result = parse_provider_name("Smith, John", "Individual")
    assert result["lastname"] == "Smith"
    assert result["firstname"] == "John"
    assert result["busname"] == ""


def test_parse_provider_name_organization() -> None:
    result = parse_provider_name("Acme Home Care LLC", "")
    assert result["busname"] == "Acme Home Care LLC"
    assert result["lastname"] == ""


def test_parse_combined_name_organization() -> None:
    result = parse_combined_name("7 Hills Healthcare Center LLC", "GROUP")
    assert result["busname"] == "7 Hills Healthcare Center LLC"
    assert result["lastname"] == ""


def test_resolve_name_fields_entity_column() -> None:
    result = resolve_name_fields(
        last_name="Active Life ADHC LLC",
        first_name="",
        last_name_is_entity_column=True,
    )
    assert result["busname"] == "Active Life ADHC LLC"
    assert result["lastname"] == ""


def test_resolve_name_fields_person_with_affiliation() -> None:
    result = resolve_name_fields(
        last_name="Smith",
        first_name="John",
        business_name="Acme Clinic LLC",
    )
    assert result["lastname"] == "Smith"
    assert result["firstname"] == "John"
    assert result["busname"] == "Acme Clinic LLC"


def test_is_organization_no_substring_false_positives() -> None:
    assert not is_organization("Vincent")
    assert not is_organization("Finch")
    assert not is_organization("Prince")
    assert not is_organization("Bradbard", "Psychologist")
    assert not is_organization("Lodmell", "MD")
    assert not looks_like_facility_name("Bradbard", "Psychologist")
    assert is_organization("Acme Inc")


def test_looks_like_facility_name_il_hills() -> None:
    assert looks_like_facility_name("7 HILLS INTEGRATED HEALTH HOME", "GROUP")
    result = parse_combined_name("7 HILLS INTEGRATED HEALTH HOME", "GROUP")
    assert result["busname"] == "7 HILLS INTEGRATED HEALTH HOME"
    assert result["lastname"] == ""


def test_looks_like_facility_name_md_urgent_care() -> None:
    assert looks_like_facility_name("Advanced Walk in Urgent Care", "")
    result = resolve_name_fields(last_name="Advanced Walk in Urgent Care", first_name="")
    assert result["busname"] == "Advanced Walk in Urgent Care"
    assert result["lastname"] == ""


def test_resolve_name_fields_md_business_entity_split_columns() -> None:
    result = resolve_name_fields(
        last_name="Abundant Life",
        first_name="Center, Inc.",
        provider_type="Business Entity",
    )
    assert result["busname"] == "Abundant Life Center, Inc."
    assert result["lastname"] == ""


def test_looks_like_facility_name_person_not_flagged() -> None:
    assert not looks_like_facility_name("FINCH ALBERT", "WAIVER SERVICE PROVIDER")
    result = parse_combined_name("FINCH ALBERT", "WAIVER SERVICE PROVIDER")
    assert result["lastname"] == "ALBERT"
    assert result["firstname"] == "FINCH"


def test_split_multi_given_first_name() -> None:
    first, mid = split_multi_given_first_name("Floyd Eric", "")
    assert first == "Floyd"
    assert mid == "Eric"
    first, mid = split_multi_given_first_name("Joseph Lynn", "A.")
    assert first == "Joseph"
    assert mid == "Lynn A."


def test_name_field_flags_org_in_person() -> None:
    flags = name_field_flags(
        {"lastname": "Smith", "firstname": "John", "midname": "", "busname": ""}
    )
    assert "org_marker_in_firstname" not in flags
    flags = name_field_flags(
        {"lastname": "", "firstname": "", "midname": "", "busname": "Acme LLC"}
    )
    assert flags == []


def test_truncate_field_preserves_long_names() -> None:
    long_name = "A" * 50
    assert truncate_field("busname", long_name) == long_name
    assert len(truncate_field("busname", long_name)) == 50

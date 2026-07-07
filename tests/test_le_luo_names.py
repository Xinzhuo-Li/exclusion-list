"""Tests for Le Luo parse_combined_name helper."""

from __future__ import annotations

from src.clean.common import parse_combined_name


def test_comma_split_last_first():
    names = parse_combined_name("Smith, John A")
    assert names["lastname"] == "Smith"
    assert names["firstname"] == "John"
    assert names["midname"] == "A"


def test_two_word_name():
    names = parse_combined_name("John Smith")
    assert names["lastname"] == "Smith"
    assert names["firstname"] == "John"


def test_one_word_name():
    names = parse_combined_name("Acme")
    assert names["lastname"] == "Acme"
    assert names["firstname"] == ""

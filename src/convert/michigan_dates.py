"""Michigan-specific sanction date parsing."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from src.clean.common import excel_serial_to_yyyymmdd, normalize_text, pd_is_na

DATE_TOKEN_RE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b")


def _fix_month_typo(month: str) -> str:
    if month == "0":
        return "10"
    return month


def _parse_date_token(month: str, day: str, year: str) -> str:
    month = _fix_month_typo(month)
    if len(year) == 2:
        year = f"20{year}" if int(year) < 50 else f"19{year}"
    try:
        return datetime(int(year), int(month), int(day)).strftime("%Y%m%d")
    except ValueError:
        return ""


def parse_michigan_date_field(value: Any) -> list[str]:
    """Extract one or more YYYYMMDD dates from a Michigan sanction date cell."""
    if value is None or pd_is_na(value):
        return []

    if isinstance(value, datetime):
        return [value.strftime("%Y%m%d")]

    if hasattr(value, "to_pydatetime"):
        try:
            converted = value.to_pydatetime()
        except (ValueError, OverflowError):
            converted = None
        if converted is not None and not pd_is_na(converted):
            return [converted.strftime("%Y%m%d")]

    text = normalize_text(value).replace("\n", " ")
    if not text:
        return []

    token_dates = [
        parsed
        for month, day, year in DATE_TOKEN_RE.findall(text)
        for parsed in [_parse_date_token(month, day, year)]
        if parsed
    ]
    if token_dates:
        return token_dates

    single = excel_serial_to_yyyymmdd(value)
    return [single] if single else []

"""Shared data cleaning utilities for OIG LEIE field mapping."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

from src.config import INDEFINITE_DATE_SERIAL, OIG_FIELD_LENGTHS

EXCEL_EPOCH = datetime(1899, 12, 30)
US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}

ORG_KEYWORDS = (
    "INC", "LLC", "LTD", "CORP", "CORPORATION", "COMPANY", "CO.",
    "GROUP", "CENTER", "CENTRE", "CLINIC", "HOSPITAL", "HOME CARE",
    "SUPPLY", "SERVICES", "SERVICE", "ORGANIZATION", "ASSOCIATES",
    "PARTNERS", "FOUNDATION", "AGENCY", "PHARMACY", "DME",
)

EXCLTYPE_MAP = {
    "OIG EXCLUSION": "OIG",
    "OIG-OIG EXCLUSION": "OIG",
    "STATE TERMINATION": "STATE",
    "MDHHS-OIG": "MDHHS-OIG",
    "MDH": "MDH",
    "LB": "LB",
    "DOM-DIVISION OF MEDICAID": "DOM",
    "ME-MEDICARE EXCLUSION": "ME",
    "F-INDIVIDUAL OR ENTITY CONVICTED OF FRAUD": "FRAUD",
}

INDEFINITE_REINDATE_VALUES = {"29991231", "99991231"}
AKA_PREFIX_RE = re.compile(r"^(?:a\.?\s*k\.?\s*a\.?\s*)", re.IGNORECASE)


def pd_is_na(value: Any) -> bool:
    if value is None:
        return True
    try:
        import pandas as pd

        return bool(pd.isna(value))
    except ImportError:
        return False


def normalize_text(value: Any) -> str:
    if value is None or pd_is_na(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return re.sub(r"\s+", " ", text)


def truncate_field(field: str, value: Any) -> str:
    """Return normalized text without length truncation.

    OIG LEIE defines max lengths in the reference schema, but we preserve full
    names and descriptions in cleaned output per project requirements.
    Fixed-format fields (NPI, ZIP, dates, state) are normalized elsewhere.
    """
    return normalize_text(value)


def clean_npi(value: Any) -> str:
    if pd_is_na(value):
        return ""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        digits = str(int(value))
    else:
        digits = re.sub(r"\D", "", normalize_text(value))
    if len(digits) == 10:
        return digits
    return ""


def excel_serial_to_yyyymmdd(value: Any) -> str:
    if value is None:
        return ""

    if pd_is_na(value):
        return ""

    if isinstance(value, datetime):
        return value.strftime("%Y%m%d")

    if hasattr(value, "to_pydatetime"):
        try:
            converted = value.to_pydatetime()
        except (ValueError, OverflowError):
            return ""
        if pd_is_na(converted):
            return ""
        return converted.strftime("%Y%m%d")

    text = normalize_text(value)
    if not text:
        return ""

    if re.fullmatch(r"\d{8}", text):
        return text

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return text.replace("-", "")

    if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{2,4}", text):
        for fmt in ("%m/%d/%Y", "%m/%d/%y"):
            try:
                return datetime.strptime(text, fmt).strftime("%Y%m%d")
            except ValueError:
                continue

    try:
        serial = int(float(text))
    except ValueError:
        return ""

    if serial == INDEFINITE_DATE_SERIAL:
        return ""

    if serial >= 400000:
        return ""

    if serial < 1 or serial > 100000:
        return ""

    try:
        return (EXCEL_EPOCH + timedelta(days=serial)).strftime("%Y%m%d")
    except OverflowError:
        return ""


def normalize_excltype(value: Any) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    upper = text.upper()
    if upper in {key.upper(): mapped for key, mapped in EXCLTYPE_MAP.items()}:
        for key, mapped in EXCLTYPE_MAP.items():
            if upper == key.upper():
                return mapped
    return text


def normalize_reindate(value: Any, exclusion_period: str = "") -> str:
    """Map Mississippi termination end dates to OIG REINDATE semantics.

    MS uses 2999-12-31 (Excel serial 401768) and text like "X - Indefinite"
    to mean the exclusion has no reinstatement/end date.
    """
    period = normalize_text(exclusion_period).lower()
    if period:
        if re.search(r"-\s*indefinite\s*$", period):
            return ""
        end_part = period.split("-")[-1].strip()
        if end_part == "indefinite":
            return ""

    if value is None or pd_is_na(value):
        return ""

    if isinstance(value, datetime) and value.year >= 2990:
        return ""

    if hasattr(value, "to_pydatetime"):
        try:
            converted = value.to_pydatetime()
            if not pd_is_na(converted) and converted.year >= 2990:
                return ""
        except (ValueError, OverflowError):
            return ""

    parsed = excel_serial_to_yyyymmdd(value)
    if parsed in INDEFINITE_REINDATE_VALUES:
        return ""
    return parsed


def parse_alias_name(name: str) -> tuple[str, str, str]:
    """Parse Montana-style alias names such as 'a.k.a. Saul Clement'."""
    text = normalize_text(name)
    if not text:
        return "", "", ""

    text = AKA_PREFIX_RE.sub("", text).strip(" ,")
    if not text:
        return "", "", ""

    if "," in text:
        return parse_last_first(text)

    parts = text.split()
    if len(parts) == 1:
        return parts[0], "", ""
    if len(parts) == 2:
        return parts[-1], parts[0], ""
    return parts[-1], parts[0], " ".join(parts[1:-1])


def normalize_zip(value: Any) -> str:
    digits = re.sub(r"\D", "", normalize_text(value))
    return digits[:5] if len(digits) >= 5 else ""


def normalize_state(value: Any, default: str = "") -> str:
    text = normalize_text(value).upper()
    if len(text) == 2 and text in US_STATE_CODES:
        return text
    match = re.search(r"\b([A-Z]{2})\b", text)
    if match and match.group(1) in US_STATE_CODES:
        return match.group(1)
    default = normalize_text(default).upper()
    return default if default in US_STATE_CODES else ""


def parse_city_state_zip(value: Any) -> tuple[str, str, str]:
    text = normalize_text(value)
    if not text:
        return "", "", ""

    zip_match = re.search(r"(\d{5}(?:-\d{4})?)\s*$", text)
    zip_code = normalize_zip(zip_match.group(1)) if zip_match else ""
    remainder = text[: zip_match.start()].strip(" ,") if zip_match else text

    state = ""
    city = remainder
    state_match = re.search(r",?\s*([A-Z]{2})\s*$", remainder, re.IGNORECASE)
    if state_match:
        state = normalize_state(state_match.group(1))
        city = remainder[: state_match.start()].strip(" ,")

    return city, state, zip_code


def is_organization(name: str, entity_hint: str = "") -> bool:
    hint = normalize_text(entity_hint).upper()
    if hint in {"ORGANIZATION", "BUSINESS ENTITY", "GROUP PRACTICE ORGANIZATION"}:
        return True
    if hint in {"INDIVIDUAL", "PERSON"}:
        return False

    upper = normalize_text(name).upper()
    if not upper:
        return False
    if any(keyword in upper for keyword in ORG_KEYWORDS):
        return True
    if hint and hint not in {"", "INDIVIDUAL", "PERSON"}:
        return False
    return False


def parse_last_first(name: str) -> tuple[str, str, str]:
    text = normalize_text(name)
    if not text:
        return "", "", ""

    if "," in text:
        last, first_part = [part.strip() for part in text.split(",", 1)]
        first_parts = first_part.split()
        first = first_parts[0] if first_parts else ""
        mid = " ".join(first_parts[1:]) if len(first_parts) > 1 else ""
        return last, first, mid

    parts = text.split()
    if len(parts) == 1:
        return parts[0], "", ""
    if len(parts) == 2:
        return parts[-1], parts[0], ""
    return parts[-1], parts[0], " ".join(parts[1:-1])


def parse_provider_name(name: str, provider_type: str = "") -> dict[str, str]:
    text = normalize_text(name)
    if not text:
        return {
            "lastname": "",
            "firstname": "",
            "midname": "",
            "busname": "",
        }

    if is_organization(text, provider_type):
        return {
            "lastname": "",
            "firstname": "",
            "midname": "",
            "busname": truncate_field("busname", text),
        }

    last, first, mid = parse_last_first(text)
    return {
        "lastname": truncate_field("lastname", last),
        "firstname": truncate_field("firstname", first),
        "midname": truncate_field("midname", mid),
        "busname": "",
    }


def build_oig_record(
    *,
    source_state: str,
    lastname: str = "",
    firstname: str = "",
    midname: str = "",
    busname: str = "",
    general: str = "",
    specialty: str = "",
    upin: str = "",
    npi: str = "",
    dob: str = "",
    address: str = "",
    city: str = "",
    state: str = "",
    zip_code: str = "",
    excltype: str = "",
    excldate: str = "",
    reindate: str = "",
    waiverdate: str = "",
    waiverstate: str = "",
) -> dict[str, str]:
    record = {
        "lastname": truncate_field("lastname", normalize_text(lastname)),
        "firstname": truncate_field("firstname", normalize_text(firstname)),
        "midname": truncate_field("midname", normalize_text(midname)),
        "busname": truncate_field("busname", normalize_text(busname)),
        "general": truncate_field("general", normalize_text(general)),
        "specialty": truncate_field("specialty", normalize_text(specialty)),
        "upin": truncate_field("upin", normalize_text(upin)),
        "npi": clean_npi(npi),
        "dob": excel_serial_to_yyyymmdd(dob),
        "address": truncate_field("address", normalize_text(address)),
        "city": truncate_field("city", normalize_text(city)),
        "state": normalize_state(state, default=source_state),
        "zip_code": normalize_zip(zip_code),
        "excltype": normalize_excltype(excltype),
        "excldate": excel_serial_to_yyyymmdd(excldate),
        "reindate": excel_serial_to_yyyymmdd(reindate),
        "waiverdate": excel_serial_to_yyyymmdd(waiverdate),
        "waiverstate": normalize_state(waiverstate),
        "source_state": source_state,
    }
    return record


def is_empty_row(values: dict[str, Any], required_any: list[str] | None = None) -> bool:
    keys = required_any or list(values.keys())
    return not any(normalize_text(values.get(key)) for key in keys)

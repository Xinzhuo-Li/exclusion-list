"""Shared data cleaning utilities for OIG LEIE field mapping."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

from src.config import INDEFINITE_DATE_SERIAL, LIST_SOURCE_STATE, OIG_FIELD_LENGTHS

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
    "PLLC", "P.L.L.C.", "DBA", "D/B/A", "ADHC", "HOSPICE",
    "NURSING", "REHAB", "REHABILITATION", "COUNSELING", "LABORATORY",
    "LAB ", " MEDICAL ", "HEALTH CARE", "HEALTHCARE",
)

# Short tokens must match as whole words (avoids Vincent→INC, Finch→INC false positives).
SHORT_ORG_TOKENS = frozenset(
    {"INC", "CORP", "LTD", "LLC", "LP", "LLP", "PLLC", "PC", "CO"}
)

# Single-word org markers: whole-word match only (avoids Bradbard→DBA, Lodmell→DME).
SINGLE_WORD_ORG_MARKERS = frozenset(
    {
        "CORPORATION",
        "COMPANY",
        "GROUP",
        "CENTER",
        "CENTRE",
        "CLINIC",
        "HOSPITAL",
        "SUPPLY",
        "SERVICES",
        "SERVICE",
        "ORGANIZATION",
        "ASSOCIATES",
        "PARTNERS",
        "FOUNDATION",
        "AGENCY",
        "PHARMACY",
        "DME",
        "ADHC",
        "HOSPICE",
        "NURSING",
        "REHAB",
        "REHABILITATION",
        "COUNSELING",
        "LABORATORY",
        "DBA",
        "HEALTHCARE",
    }
)

# Multi-word phrases: safe to substring-match on normalized uppercase text.
MULTI_WORD_ORG_PHRASES = (
    "HOME CARE",
    "HEALTH CARE",
    "D/B/A",
    "P.L.L.C.",
    " MEDICAL ",
    " LAB ",
)

ENTITY_ORG_HINTS = frozenset(
    {"ORGANIZATION", "BUSINESS ENTITY", "GROUP PRACTICE ORGANIZATION"}
)

ORG_SUFFIX_RE = re.compile(
    r"\b(?:LLC|L\.L\.C\.|INC|INC\.|CORP|CORP\.|LTD|LTD\.|LP|LLP|PLLC|P\.L\.C\.|PC|P\.C\.)\b",
    re.IGNORECASE,
)

# Whole-word tokens common in facility names (not substring-matched — avoids Finch/Vincent false positives).
FACILITY_WORDS = frozenset(
    {
        "HEALTH",
        "HOME",
        "HOMES",
        "CARE",
        "CENTER",
        "CENTRE",
        "CLINIC",
        "HOSPITAL",
        "URGENT",
        "MEDICAL",
        "DENTAL",
        "PHARMACY",
        "NURSING",
        "HOSPICE",
        "REHAB",
        "SERVICES",
        "SERVICE",
        "GROUP",
        "ASSOCIATES",
        "PARTNERS",
        "SUPPLY",
        "INTEGRATED",
        "TRANSIT",
        "TRANSPORT",
        "THERAPY",
        "FOUNDATION",
        "AGENCY",
        "INCORPORATED",
        "CORPORATION",
        "WALK",
        "HILLS",
        "FACILITY",
        "FACILITIES",
        "ENTERPRISES",
        "SOLUTIONS",
    }
)

FACILITY_PHRASES = (
    "URGENT CARE",
    "HOME HEALTH",
    "HEALTH CARE",
    "WALK IN",
    "HOME CARE",
    "NURSING HOME",
    "MENTAL HEALTH",
    "INTEGRATED HEALTH",
)

# Facility-signal words used with short (2–3 word) names like "AMEGROW INCORPORATED".
STRONG_FACILITY_WORDS = frozenset(
    {
        "INCORPORATED",
        "CORPORATION",
        "TRANSIT",
        "HEALTH",
        "HOME",
        "CENTER",
        "CENTRE",
        "CLINIC",
        "HOSPITAL",
        "PHARMACY",
        "SERVICES",
        "INTEGRATED",
        "CARE",
        "URGENT",
        "HILLS",
        "FACILITY",
    }
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


def extract_first_npi(value: Any) -> str:
    """Return first 10-digit NPI from a field that may list multiple IDs."""
    text = normalize_text(value)
    if not text:
        return ""
    matches = re.findall(r"\b\d{10}\b", text)
    if matches:
        return matches[0]
    return clean_npi(value)


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


def entity_type_is_organization(entity_hint: str) -> bool:
    return normalize_text(entity_hint).upper() in ENTITY_ORG_HINTS


def text_has_org_marker(text: str) -> bool:
    """Return True when text contains a business-entity marker (word-safe for short tokens)."""
    upper = normalize_text(text).upper()
    if not upper:
        return False
    if ORG_SUFFIX_RE.search(upper):
        return True
    for token in SHORT_ORG_TOKENS | SINGLE_WORD_ORG_MARKERS:
        if re.search(rf"\b{re.escape(token)}\b\.?", upper):
            return True
    if re.search(r"\bCO\.\b", upper):
        return True
    return any(phrase in upper for phrase in MULTI_WORD_ORG_PHRASES)


def is_organization(name: str, entity_hint: str = "") -> bool:
    hint = normalize_text(entity_hint).upper()
    if entity_type_is_organization(hint):
        return True
    if hint in {"INDIVIDUAL", "PERSON"}:
        return False

    if not normalize_text(name):
        return False
    if text_has_org_marker(name):
        return True
    if hint and hint not in {"", "INDIVIDUAL", "PERSON"}:
        return False
    return False


def looks_like_facility_name(name: str, entity_hint: str = "") -> bool:
    """Heuristic: multi-word practice/facility name that should map to busname.

    Used when sources put facility names in a person column or a combined provider_name
    without LLC/INC suffixes (e.g. IL '7 HILLS INTEGRATED HEALTH HOME', MD 'Advanced Walk in Urgent Care').

    Comma-separated 'Last, First' strings are treated as persons and return False.
    Entity-type hints alone do not classify a name fragment as a facility.
    """
    if text_has_org_marker(name):
        return True

    text = normalize_text(name)
    if not text or "," in text:
        return False

    upper = text.upper()
    words = upper.split()

    if any(phrase in upper for phrase in FACILITY_PHRASES):
        return True

    # Numbered facility names: "7 HILLS INTEGRATED HEALTH HOME"
    if words and words[0].isdigit() and len(words) >= 3:
        if any(w in FACILITY_WORDS for w in words[1:]):
            return True

    if len(words) >= 2 and any(w in STRONG_FACILITY_WORDS for w in words):
        return True

    if len(words) >= 4 and any(w in FACILITY_WORDS for w in words):
        return True

    return False


def split_multi_given_first_name(first: str, mid: str = "") -> tuple[str, str]:
    """Split multiple given names in a first_name column (e.g. LA 'Floyd Eric' + last 'Holmes')."""
    text = normalize_text(first)
    extra_mid = normalize_text(mid)
    if not text:
        return "", extra_mid
    parts = text.split()
    if len(parts) <= 1:
        return text, extra_mid
    first_part = parts[0]
    middle_parts = parts[1:]
    if extra_mid:
        middle_parts.append(extra_mid)
    return first_part, " ".join(middle_parts)


def _empty_name_fields() -> dict[str, str]:
    return {"lastname": "", "firstname": "", "midname": "", "busname": ""}


def _person_name_fields(
    *,
    last: str = "",
    first: str = "",
    mid: str = "",
    bus: str = "",
) -> dict[str, str]:
    return {
        "lastname": truncate_field("lastname", last),
        "firstname": truncate_field("firstname", first),
        "midname": truncate_field("midname", mid),
        "busname": truncate_field("busname", bus),
    }


def _business_name_fields(name: str) -> dict[str, str]:
    return {**_empty_name_fields(), "busname": truncate_field("busname", name)}


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


def parse_combined_name(name: str, provider_type: str = "") -> dict[str, str]:
    """Split a combined provider name into person fields or busname."""
    text = normalize_text(name)
    if not text:
        return _empty_name_fields()

    if looks_like_facility_name(text, provider_type):
        return _business_name_fields(text)

    if is_organization(text, provider_type):
        return _business_name_fields(text)

    if "," in text:
        parts = [p.strip() for p in text.split(",")]
        last = parts[0]
        rest = parts[1].split() if len(parts) > 1 else []
        first = rest[0] if rest else ""
        mid = " ".join(rest[1:]) if len(rest) > 1 else ""
        return _person_name_fields(last=last, first=first, mid=mid)

    words = text.split()
    if len(words) == 1:
        return _person_name_fields(last=words[0])
    if len(words) == 2:
        return _person_name_fields(last=words[1], first=words[0])
    if len(words) == 3:
        return _person_name_fields(last=words[2], first=words[0], mid=words[1])
    return _person_name_fields(
        last=words[-1],
        first=words[0],
        mid=" ".join(words[1:-1]),
    )


def resolve_name_fields(
    *,
    provider_name: Any = "",
    last_name: Any = "",
    first_name: Any = "",
    mid_name: Any = "",
    business_name: Any = "",
    provider_type: Any = "",
    last_name_is_entity_column: bool = False,
    split_multi_given_first_names: bool = False,
) -> dict[str, str]:
    """Normalize person vs business identity from heterogeneous state sources.

    New state converters should call this instead of hand-mapping name columns.
    See docs/NAME_HANDLING.md for column semantics and flags.
    """
    bus = normalize_text(business_name)
    last = normalize_text(last_name)
    first = normalize_text(first_name)
    mid = normalize_text(mid_name)
    pname = normalize_text(provider_name)
    ptype = normalize_text(provider_type)

    if pname and not last and not first and not mid:
        parsed = parse_combined_name(pname, ptype)
        if bus and not parsed["busname"]:
            if parsed["lastname"] or parsed["firstname"]:
                parsed["busname"] = truncate_field("busname", bus)
            elif not parsed["busname"]:
                parsed["busname"] = truncate_field("busname", bus)
        return parsed

    if bus and not last and not first and not pname:
        if "," in bus and not is_organization(bus, ptype):
            return parse_combined_name(bus, ptype)
        return _business_name_fields(bus)

    if entity_type_is_organization(ptype):
        combined = " ".join(part for part in (last, first, mid) if part).strip()
        if combined:
            return _business_name_fields(combined)

    if last and not first:
        if (
            last_name_is_entity_column
            or looks_like_facility_name(last, ptype)
            or is_organization(last, ptype)
        ):
            return _business_name_fields(last)

    if last and is_organization(last, ptype) and not is_organization(f"{first} {last}".strip(), ptype):
        return _business_name_fields(last)

    if last or first:
        if split_multi_given_first_names and first and last:
            first, mid = split_multi_given_first_name(first, mid)
        return _person_name_fields(last=last, first=first, mid=mid, bus=bus)

    if bus:
        return _business_name_fields(bus)

    return _empty_name_fields()


def name_field_flags(record: dict[str, str]) -> list[str]:
    """Return audit flags for a cleaned OIG record's name fields (non-blocking QA)."""
    flags: list[str] = []
    last = normalize_text(record.get("lastname"))
    first = normalize_text(record.get("firstname"))
    mid = normalize_text(record.get("midname"))
    bus = normalize_text(record.get("busname"))

    if not any((last, first, mid, bus)):
        flags.append("empty_all_names")
        return flags

    if not bus:
        for field, value in (
            ("lastname", last),
            ("firstname", first),
            ("midname", mid),
        ):
            if value and looks_like_facility_name(value, record.get("general", "")):
                flags.append(f"facility_in_{field}")
            elif value and is_organization(value):
                flags.append(f"org_marker_in_{field}")
            if len(value.split()) >= 4:
                flags.append(f"long_unsplit_in_{field}")

        person_text = " ".join(part for part in (first, mid, last) if part)
        if person_text and len(person_text.split()) == 1 and last and not first:
            flags.append("one_word_person")

    return flags


def parse_provider_name(name: str, provider_type: str = "") -> dict[str, str]:
    return parse_combined_name(name, provider_type)


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
    list_source: str = LIST_SOURCE_STATE,
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
        "list_source": list_source if list_source in ("federal", "state") else LIST_SOURCE_STATE,
        "source_state": source_state,
    }
    return record


def is_empty_row(values: dict[str, Any], required_any: list[str] | None = None) -> bool:
    keys = required_any or list(values.keys())
    return not any(normalize_text(values.get(key)) for key in keys)

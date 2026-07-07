"""Audit conversion quality by comparing source files to cleaned OIG output."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pdfplumber

from src.clean.common import (
    build_oig_record,
    clean_npi,
    excel_serial_to_yyyymmdd,
    is_organization,
    normalize_text,
    parse_city_state_zip,
    parse_last_first,
    parse_provider_name,
    truncate_field,
)
from src.config import CLEANED_DIR, RAW_DIR, artifact_run_dir
from src.convert.maryland import load_raw as load_md, to_oig_records as md_to_oig
from src.convert.massachusetts import load_raw as load_ma, to_oig_records as ma_to_oig
from src.convert.michigan import load_raw as load_mi, to_oig_records as mi_to_oig
from src.convert.mississippi import load_raw as load_ms, to_oig_records as ms_to_oig
from src.convert.montana import load_raw as load_mt, to_oig_records as mt_to_oig
from src.convert.nebraska import load_raw as load_ne, to_oig_records as ne_to_oig

DATE_RE = re.compile(r"^\d{8}$")
NPI_RE = re.compile(r"^\d{10}$")


def _read_cleaned(state: str) -> list[dict[str, str]]:
    path = CLEANED_DIR / f"{state}_oig.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


from src.convert.base import record_identity_key


def _compare_reruns(
    state: str,
    loader,
    converter,
    cleaned_rows: list[dict[str, str]],
) -> dict[str, Any]:
    raw_df = loader()
    rerun_records = converter(raw_df)
    rerun_by_key = {record_identity_key(r): r for r in rerun_records}

    cleaned_by_key: dict[str, dict[str, str]] = {}
    duplicate_keys: list[str] = []
    for row in cleaned_rows:
        key = record_identity_key(row)
        if key in cleaned_by_key:
            duplicate_keys.append(key)
        cleaned_by_key[key] = row

    missing_in_csv = [k for k in rerun_by_key if k not in cleaned_by_key]
    extra_in_csv = [k for k in cleaned_by_key if k not in rerun_by_key]
    field_mismatches: list[dict[str, Any]] = []

    for key, expected in rerun_by_key.items():
        actual = cleaned_by_key.get(key)
        if not actual:
            continue
        for field in expected:
            if expected.get(field, "") != actual.get(field, ""):
                field_mismatches.append(
                    {
                        "key": key,
                        "field": field,
                        "expected": expected.get(field, ""),
                        "actual": actual.get(field, ""),
                    }
                )

    return {
        "state": state.upper(),
        "raw_rows": len(raw_df),
        "rerun_cleaned": len(rerun_records),
        "csv_cleaned": len(cleaned_rows),
        "missing_in_csv": len(missing_in_csv),
        "extra_in_csv": len(extra_in_csv),
        "duplicate_keys_in_csv": len(duplicate_keys),
        "field_mismatches": len(field_mismatches),
        "field_mismatch_samples": field_mismatches[:5],
        "missing_samples": missing_in_csv[:5],
        "extra_samples": extra_in_csv[:5],
        "consistent": (
            not missing_in_csv
            and not extra_in_csv
            and not field_mismatches
            and len(rerun_records) == len(cleaned_rows)
        ),
    }


def _source_vs_processed_counts() -> list[dict[str, Any]]:
    specs = {
        "md": ("Maryland.xlsx", {"header": 0}),
        "ma": ("Massachusetts.xlsx", {"header": 0}),
        "mi": ("Michigan.xlsx", {"header": 1}),
        "ms": ("Mississippi.xlsx", {"header": 8}),
        "mt": ("Montana.xlsx", {"header": 0}),
    }
    results = []
    for code, (fname, kwargs) in specs.items():
        src = pd.read_excel(RAW_DIR / fname, **kwargs).dropna(how="all")
        proc = pd.read_csv(CLEANED_DIR.parent / "processed" / f"{code}_raw.csv")
        results.append(
            {
                "state": code.upper(),
                "source_rows": len(src),
                "processed_rows": len(proc),
                "delta": len(src) - len(proc),
            }
        )

    ne_table_rows = 0
    with pdfplumber.open(RAW_DIR / "Nebraska.pdf") as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                for row in table:
                    if row and normalize_text(row[0]).lower() != "date added to nmep":
                        ne_table_rows += 1
    ne_proc = pd.read_csv(CLEANED_DIR.parent / "processed" / f"ne_raw.csv")
    results.append(
        {
            "state": "NE",
            "source_rows": ne_table_rows,
            "processed_rows": len(ne_proc),
            "delta": ne_table_rows - len(ne_proc),
        }
    )
    return results


def _spot_check_samples() -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []

    md = load_md()
    md_clean = _read_cleaned("md")
    for idx in [0, 3, 5, 100]:
        row = md.iloc[idx].to_dict()
        clean = md_clean[idx]
        city, state, zip_code = parse_city_state_zip(row.get("city_state_zip"))
        org = normalize_text(row.get("last_name_org"))
        fn = normalize_text(row.get("first_name"))
        samples.append(
            {
                "state": "MD",
                "row": idx + 2,
                "source_name": f"{org} / {fn}",
                "source_npi": clean_npi(row.get("npi")),
                "source_date": excel_serial_to_yyyymmdd(row.get("termination_date")),
                "clean_npi": clean.get("npi"),
                "clean_date": clean.get("excldate"),
                "clean_name": f"{clean.get('lastname')} / {clean.get('firstname')} / {clean.get('busname')}",
                "match": (
                    clean_npi(row.get("npi")) == clean.get("npi")
                    and excel_serial_to_yyyymmdd(row.get("termination_date"))
                    == clean.get("excldate")
                ),
            }
        )

    ma = load_ma()
    ma_clean = _read_cleaned("ma")
    for idx in [0, 1, 2, 50]:
        row = ma.iloc[idx].to_dict()
        clean = ma_clean[idx]
        names = parse_provider_name(row.get("provider_name"), row.get("provider_type"))
        samples.append(
            {
                "state": "MA",
                "row": idx + 2,
                "source_name": row.get("provider_name"),
                "source_npi": clean_npi(row.get("npi")),
                "source_date": excel_serial_to_yyyymmdd(row.get("effective_date")),
                "clean_npi": clean.get("npi"),
                "clean_date": clean.get("excldate"),
                "clean_name": f"{names['lastname']}/{names['firstname']}/{names['busname']}",
                "parsed_name": f"{clean.get('lastname')}/{clean.get('firstname')}/{clean.get('busname')}",
                "match": (
                    clean_npi(row.get("npi")) == clean.get("npi")
                    and excel_serial_to_yyyymmdd(row.get("effective_date"))
                    == clean.get("excldate")
                ),
            }
        )

    return samples


def _format_checks(cleaned_rows: list[dict[str, str]], state: str) -> dict[str, Any]:
    npi_vals = [r.get("npi", "") for r in cleaned_rows]
    date_vals = [r.get("excldate", "") for r in cleaned_rows]
    invalid_npi = [v for v in npi_vals if v and not NPI_RE.match(v)]
    invalid_dates = [v for v in date_vals if v and not DATE_RE.match(v)]
    empty_name = [
        r
        for r in cleaned_rows
        if not r.get("lastname") and not r.get("busname")
    ]
    long_busname = [
        r for r in cleaned_rows if r.get("busname") and len(r.get("busname", "")) > 30
    ]
    return {
        "state": state.upper(),
        "invalid_npi_count": len(invalid_npi),
        "invalid_date_count": len(invalid_dates),
        "empty_name_count": len(empty_name),
        "long_busname_count": len(long_busname),
        "empty_name_samples": empty_name[:3],
        "long_busname_samples": [r.get("busname") for r in long_busname[:5]],
    }


def run() -> dict[str, Any]:
    states = [
        ("md", load_md, md_to_oig),
        ("ma", load_ma, ma_to_oig),
        ("mi", load_mi, mi_to_oig),
        ("ms", load_ms, ms_to_oig),
        ("mt", load_mt, mt_to_oig),
        ("ne", load_ne, ne_to_oig),
    ]

    rerun_checks = []
    format_checks = []
    for code, loader, converter in states:
        cleaned = _read_cleaned(code)
        rerun_checks.append(_compare_reruns(code, loader, converter, cleaned))
        format_checks.append(_format_checks(cleaned, code))

    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "all_reruns_consistent": all(r["consistent"] for r in rerun_checks),
            "total_cleaned_records": sum(r["csv_cleaned"] for r in rerun_checks),
        },
        "source_vs_processed_counts": _source_vs_processed_counts(),
        "rerun_consistency": rerun_checks,
        "format_checks": format_checks,
        "spot_checks": _spot_check_samples(),
        "known_limitations": [
            "Name fields are preserved in full (TEXT); OIG max lengths are reference only.",
            "Deduplication removes only exact duplicates (all identity fields identical).",
            "Cross-state duplicate NPIs are retained as separate rows per business policy.",
            "Empty EXCLDATE means long-term exclusion; no placeholder dates are inserted.",
            "MS rows with missing key fields are dropped during cleaning.",
            "NE PDF table extraction may include rows not present in a simple row count.",
            "Name parsing for individuals vs organizations is heuristic and may differ from source intent.",
        ],
    }

    run_dir = artifact_run_dir()
    out = run_dir / f"quality_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with out.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, default=str)

    print("=== QUALITY AUDIT SUMMARY ===")
    for item in report["source_vs_processed_counts"]:
        flag = "OK" if item["delta"] == 0 else f"DELTA {item['delta']}"
        print(
            f"{item['state']}: source={item['source_rows']} processed={item['processed_rows']} [{flag}]"
        )
    for item in rerun_checks:
        status = "CONSISTENT" if item["consistent"] else "INCONSISTENT"
        print(
            f"{item['state']}: {status} raw={item['raw_rows']} cleaned={item['csv_cleaned']} "
            f"missing={item['missing_in_csv']} extra={item['extra_in_csv']} "
            f"field_mismatches={item['field_mismatches']}"
        )
    for item in format_checks:
        print(
            f"{item['state']}: invalid_npi={item['invalid_npi_count']} "
            f"invalid_date={item['invalid_date_count']} empty_name={item['empty_name_count']} "
            f"long_busname={item['long_busname_count']}"
        )
    print(f"Report: {out}")
    return report


if __name__ == "__main__":
    run()

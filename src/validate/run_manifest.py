"""Record source file fingerprints at pipeline start for auditability."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from src.config import ACTIVE_SOURCE_STATES, RAW_DIR, artifact_run_dir

STATE_RAW_FILES = {
    "md": "Maryland.xlsx",
    "ma": "Massachusetts.xlsx",
    "mi": "Michigan.xlsx",
    "ms": "Mississippi.xlsx",
    "mt": "Montana.xlsx",
    "ne": "Nebraska.pdf",
    "ca": "California.csv",
    "ny": "NewYork.xlsx",
    "nc": "NorthCarolina.xlsx",
    "nd": "NorthDakota.xlsx",
    "oh": "Ohio.xlsx",
    "nj": "NewJersey.csv",
    "pa": "Pennsylvania.csv",
    "ga": "Georgia.xlsx",
    "hi": "Hawaii.pdf",
    "id": "Idaho.pdf",
    "il": "Illinois.xlsx",
    "in": "Indiana.xlsx",
    "ia": "Iowa.xlsx",
    "ks": "Kansas.xlsx",
    "ky": "Kentucky.xlsx",
    "la": "Louisiana.xlsx",
    "me": "Maine.pdf",
}

FEDERAL_RAW_FILE = "LEIE.csv"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_row_hint(path: Path) -> int | None:
    """Best-effort row count for common source formats."""
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        try:
            import pandas as pd

            return len(pd.read_excel(path))
        except Exception:
            return None
    if suffix == ".pdf":
        try:
            import pdfplumber

            count = 0
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        count += max(len(table) - 1, 0)
            return count
        except Exception:
            return None
    if suffix == ".csv":
        try:
            import csv

            with path.open(newline="", encoding="utf-8-sig") as handle:
                return sum(1 for _ in csv.DictReader(handle))
        except Exception:
            return None
    return None


def _manifest_entry(filename: str, *, label: str) -> dict:
    path = RAW_DIR / filename
    entry: dict = {
        "label": label,
        "filename": filename,
        "path": str(path),
        "exists": path.exists(),
    }
    if path.exists():
        entry["sha256"] = _sha256(path)
        entry["size_bytes"] = path.stat().st_size
        row_hint = _file_row_hint(path)
        if row_hint is not None:
            entry["source_row_hint"] = row_hint
    return entry


def write_run_manifest(*, skip_nebraska: bool = False, include_pending: bool = False) -> Path:
    del include_pending  # legacy flag; all states are active now
    entries: list[dict] = []
    for state, filename in STATE_RAW_FILES.items():
        if skip_nebraska and state == "ne":
            continue
        entry = _manifest_entry(filename, label=state.upper())
        entry["state"] = state.upper()
        entries.append(entry)

    leie_path = RAW_DIR / FEDERAL_RAW_FILE
    if leie_path.exists():
        federal_entry = _manifest_entry(FEDERAL_RAW_FILE, label="OIG")
        federal_entry["list_source"] = "federal"
        entries.append(federal_entry)

    payload = {
        "generated_at": datetime.now().isoformat(),
        "raw_dir": str(RAW_DIR),
        "active_states": ACTIVE_SOURCE_STATES,
        "files": entries,
    }
    run_dir = artifact_run_dir()
    out = run_dir / f"run_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with out.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(f"Run manifest written to {out}")
    return out

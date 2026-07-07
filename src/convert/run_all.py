"""Run all state conversion and cleaning pipelines."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STATE_MODULES = [
    "src.convert.maryland",
    "src.convert.mississippi",
    "src.convert.montana",
    "src.convert.massachusetts",
    "src.convert.michigan",
    "src.convert.nebraska",
    "src.convert.north_carolina",
    "src.convert.north_dakota",
    "src.convert.ohio",
    "src.convert.new_jersey",
    "src.convert.new_york",
    "src.convert.pennsylvania",
    "src.convert.california",
    "src.convert.georgia",
    "src.convert.hawaii",
    "src.convert.idaho",
    "src.convert.illinois",
    "src.convert.indiana",
    "src.convert.iowa",
    "src.convert.kansas",
    "src.convert.kentucky",
    "src.convert.louisiana",
    "src.convert.maine",
    "src.convert.alabama",
    "src.convert.alaska",
    "src.convert.arizona",
    "src.convert.arkansas",
    "src.convert.colorado",
    "src.convert.connecticut",
    "src.convert.delaware",
    "src.convert.district_of_columbia",
    "src.convert.florida",
    "src.convert.south_carolina",
    "src.convert.tennessee",
    "src.convert.texas",
    "src.convert.vermont",
    "src.convert.washington",
    "src.convert.west_virginia",
    "src.convert.wyoming",
]

PENDING_STATE_MODULES: list[str] = []


def run_all(skip_nebraska: bool = False, skip_federal: bool = False) -> dict[str, tuple[int, int]]:
    results: dict[str, tuple[int, int]] = {}
    for module_name in STATE_MODULES:
        if skip_nebraska and module_name.endswith("nebraska"):
            continue
        module = importlib.import_module(module_name)
        raw_df, cleaned = module.run()
        state = module.SOURCE_STATE
        results[state] = (len(raw_df), len(cleaned))
        print(f"{state}: {len(raw_df)} processed, {len(cleaned)} cleaned")

    if skip_federal:
        return results

    from src.config import RAW_DIR

    if (RAW_DIR / "LEIE.csv").exists():
        from src.convert import federal_leie

        raw_df, cleaned = federal_leie.run()
        results["OIG"] = (len(raw_df), len(cleaned))
        print(f"OIG: {len(raw_df)} processed, {len(cleaned)} cleaned federal LEIE")

    return results


if __name__ == "__main__":
    skip_ne = "--skip-nebraska" in sys.argv
    skip_fed = "--states-only" in sys.argv
    run_all(skip_nebraska=skip_ne, skip_federal=skip_fed)

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
]


def run_all(skip_nebraska: bool = False) -> dict[str, tuple[int, int]]:
    results: dict[str, tuple[int, int]] = {}
    for module_name in STATE_MODULES:
        if skip_nebraska and module_name.endswith("nebraska"):
            continue
        module = importlib.import_module(module_name)
        raw_df, cleaned = module.run()
        state = module.SOURCE_STATE
        results[state] = (len(raw_df), len(cleaned))
        print(f"{state}: {len(raw_df)} processed, {len(cleaned)} cleaned")
    return results


if __name__ == "__main__":
    skip_ne = "--skip-nebraska" in sys.argv
    run_all(skip_nebraska=skip_ne)

# Source Files (`data/raw/`)

Place the six state Medicaid exclusion/sanction source files here. **Filenames are case-sensitive** and must match exactly.

| State | Code | Required filename | Format |
|-------|------|-------------------|--------|
| Maryland | MD | `Maryland.xlsx` | Excel |
| Massachusetts | MA | `Massachusetts.xlsx` | Excel |
| Michigan | MI | `Michigan.xlsx` | Excel |
| Mississippi | MS | `Mississippi.xlsx` | Excel |
| Montana | MT | `Montana.xlsx` | Excel |
| Nebraska | NE | `Nebraska.pdf` | PDF (table extraction) |

These seven files are included in the GitHub repository for reproducibility. The pipeline reads them directly — it does **not** accept CSV exports in this folder.

## Optional reference

| File | Purpose |
|------|---------|
| `数据结构.pdf` | OIG LEIE target schema reference (not used by the ETL code) |

## After updating source files

1. Run the full pipeline: `python3 -m src.pipeline --skip-db` (or without `--skip-db` if loading to PostgreSQL).
2. Check `docs/run_manifest_*.json` for SHA256 fingerprints of the files used in that run.
3. If record counts change intentionally, update `STATE_EXPECTATIONS` in `src/validate/check_import.py` and the counts in `docs/DATA_INVENTORY.md`.

See [docs/WORKFLOW.md](../docs/WORKFLOW.md) for the full step-by-step guide.

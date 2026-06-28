# Six-State Medical Exclusion List ETL

ETL pipeline that merges Maryland, Massachusetts, Michigan, Mississippi, Montana, and Nebraska Medicaid exclusion lists into PostgreSQL using the OIG LEIE schema.

**Repository:** https://github.com/Xinzhuo-Li/medicaid-exclusion-list

**Requirements:** Python 3.10+, pip. PostgreSQL 12+ is optional (needed only for database load/merge).

---

## Quick Start

### Path A — Full ETL (convert + validate + PostgreSQL)

```bash
git clone https://github.com/Xinzhuo-Li/medicaid-exclusion-list.git
cd medicaid-exclusion-list
pip3 install -r requirements.txt
cp .env.example .env          # edit PostgreSQL credentials
python3 -m pytest tests/ -q   # optional sanity check
python3 -m src.pipeline
```

### Path B — CSV only (no database)

Useful for verifying converts and validations without PostgreSQL:

```bash
git clone https://github.com/Xinzhuo-Li/medicaid-exclusion-list.git
cd medicaid-exclusion-list
pip3 install -r requirements.txt
python3 -m pytest tests/ -q
python3 -m src.pipeline --skip-db
```

---

## Project Structure

```
medicaid-exclusion-list/
├── data/
│   ├── raw/              # Source xlsx/pdf (7 files — see data/raw/README.md)
│   ├── processed/        # State-native CSV (*_raw.csv)
│   └── cleaned/          # OIG-mapped CSV (*_oig.csv)
├── docs/
│   ├── WORKFLOW.md       # Detailed step-by-step runbook
│   ├── DATA_INVENTORY.md
│   ├── STATE_MAPPING.md
│   └── ISSUES_AND_DECISIONS_BILINGUAL.md
├── sql/
│   ├── 01_create_stage_tables.sql
│   ├── 02_create_main_table.sql
│   ├── 03_merge_to_main.sql
│   └── 04_verify_main_sync.sql
├── src/
│   ├── clean/            # Shared cleaning utilities
│   ├── convert/          # Per-state converters
│   ├── load/             # PostgreSQL loader
│   ├── validate/         # Validation, audit, run manifest
│   └── pipeline.py       # End-to-end orchestrator
├── tests/                # pytest regression tests
├── deploy/               # Optional remote server scripts
├── requirements.txt
└── .env.example
```

---

## Source Data

Seven source files must be present in `data/raw/` (included in the repo):

| State | File |
|-------|------|
| MD | `Maryland.xlsx` |
| MA | `Massachusetts.xlsx` |
| MI | `Michigan.xlsx` |
| MS | `Mississippi.xlsx` |
| MT | `Montana.xlsx` |
| NE | `Nebraska.pdf` |

See [data/raw/README.md](data/raw/README.md) for details. The pipeline reads **xlsx/pdf only** — not CSV — from this folder.

Pre-generated outputs in `data/processed/` and `data/cleaned/` allow running validation and tests without re-converting.

---

## Pipeline (Steps 0–5)

```bash
python3 -m src.pipeline [OPTIONS]
```

| Step | What it does | Output |
|------|--------------|--------|
| **0** | Record source file SHA256 | `docs/run_manifest_*.json` |
| **1** | Convert & clean all states | `data/processed/*`, `data/cleaned/*` |
| **2** | Validate row counts & field quality | `docs/validation_report_*.json` — **fail-fast** |
| **3** | Rerun consistency audit | `docs/quality_audit_*.json` — **fail-fast** |
| **4** | Load PostgreSQL stage + staging | `stage_*`, `cleaned_staging` tables |
| **5** | Merge to `exclusion_main` + sync verify | Strict EXCEPT check — **fail-fast** |

### CLI flags

| Flag | Description |
|------|-------------|
| `--skip-nebraska` | Skip Nebraska PDF in Steps 0–1 |
| `--skip-db` | Stop after Step 3 (no PostgreSQL) |
| `--skip-merge` | Load tables but do not merge into `exclusion_main` |

For manual step-by-step commands, see [docs/WORKFLOW.md](docs/WORKFLOW.md).

---

## Environment Setup

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `PGHOST` | PostgreSQL host | `localhost` |
| `PGPORT` | PostgreSQL port | `5432` |
| `PGDATABASE` | Database name | `exclusion_list` |
| `PGUSER` | Database user | `postgres` |
| `PGPASSWORD` | Database password | *(required)* |

Create the database before the first full run:

```bash
createdb exclusion_list
```

Schema (`01_create_stage_tables.sql`, `02_create_main_table.sql`) is applied automatically by `load_to_postgres`.

---

## Testing

```bash
python3 -m pytest tests/ -v
```

Tests cover date/NPI/name transforms, Michigan multi-date expansion, Mississippi REINDATE rules, deduplication, and record-count regression against baselines in `docs/DATA_INVENTORY.md`.

---

## Expected Record Counts

| State | Source rows | Cleaned records |
|-------|-------------|-----------------|
| MD | 1,605 | 1,603 |
| MA | 294 | 294 |
| MI | 3,982 | 4,921 |
| MS | 194 | 193 |
| MT | 174 | 174 |
| NE | 1,391 | 1,390 |
| **Total** | **7,640** | **8,575** |

Michigan produces more cleaned records than source rows because dual sanction dates expand into separate records.

---

## Target Schema (OIG LEIE)

18 OIG fields plus `source_state`:

`lastname, firstname, midname, busname, general, specialty, upin, npi, dob, address, city, state, zip_code, excltype, excldate, reindate, waiverdate, waiverstate, source_state`

Name fields use PostgreSQL `TEXT` (full length preserved). See [docs/STATE_MAPPING.md](docs/STATE_MAPPING.md).

---

## Output Artifacts

| Artifact | Location |
|----------|----------|
| Run manifest (source file hashes) | `docs/run_manifest_*.json` |
| Validation report | `docs/validation_report_*.json` |
| Quality audit | `docs/quality_audit_*.json` |
| Dedup dropped records | `docs/dedup_dropped_{state}.json` |

---

## Troubleshooting

| Problem | What to do |
|---------|------------|
| Missing raw file | Ensure all seven files in `data/raw/` with exact names — see [data/raw/README.md](data/raw/README.md) |
| Validation failed | Read latest `docs/validation_report_*.json`; check `"checks"` for failing state |
| Quality audit failed | Re-run convert: `python3 -m src.convert.run_all` |
| Database connection error | Verify `.env`; test with `psql -h $PGHOST -U $PGUSER -d $PGDATABASE` |
| Sync verification failed | Re-run merge: `psql ... -f sql/03_merge_to_main.sql` |

More detail: [docs/WORKFLOW.md](docs/WORKFLOW.md).

---

## Deployment (Optional)

Remote server sync scripts live in `deploy/`. Copy `deploy/config.example.sh` to `deploy/config.sh` (gitignored) and set your SSH host and paths.

```bash
cp deploy/config.example.sh deploy/config.sh
# edit DEPLOY_HOST, DEPLOY_REMOTE_DIR, PGPORT
```

---

## Further Reading

- [docs/WORKFLOW.md](docs/WORKFLOW.md) — full operator runbook
- [docs/DATA_INVENTORY.md](docs/DATA_INVENTORY.md) — columns and data quality
- [docs/STATE_MAPPING.md](docs/STATE_MAPPING.md) — per-state field mapping
- [docs/ISSUES_AND_DECISIONS_BILINGUAL.md](docs/ISSUES_AND_DECISIONS_BILINGUAL.md) — business rules (EN + 中文)

---

## Notes

- Nebraska PDF is parsed via `pdfplumber` table extraction (no OCR).
- Excel dates are converted to `YYYYMMDD`.
- Mississippi indefinite exclusion end dates map to empty `REINDATE`.
- Cross-state duplicate NPIs are retained as separate rows (see issues doc).

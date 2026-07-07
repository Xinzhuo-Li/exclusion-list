# 39-State Medicaid Exclusion List ETL + Federal LEIE

ETL pipeline merging **39 state** Medicaid exclusion lists and **HHS OIG LEIE** into PostgreSQL using the OIG LEIE schema. Includes Django web search (`web/`).

**Repository:** https://github.com/Xinzhuo-Li/medicaid-exclusion-list

**Requirements:** Python 3.10+, pip. PostgreSQL 12+ optional (database load/merge only).

**Production baseline (2026-07):** 173,312 state rows + 83,464 federal = **256,776** total in `exclusion_main`.

---

## Quick Start

```bash
git clone https://github.com/Xinzhuo-Li/medicaid-exclusion-list.git
cd medicaid-exclusion-list
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit PostgreSQL credentials
python3 -m pytest tests/ -q   # optional sanity check
python3 -m src.pipeline --skip-db   # CSV + validate (no DB)
python3 -m src.pipeline             # full ETL + PostgreSQL
```

---

## Project Structure

```
medicaid-exclusion-list/
├── data/
│   ├── raw/              # 42 source files — see data/raw/README.md
│   ├── processed/        # State-native CSV (*_raw.csv)
│   └── cleaned/          # OIG-mapped CSV (*_oig.csv) + federal_oig.csv
├── sources/
│   ├── CONTRIBUTORS.yaml # Single contributor → state registry
│   └── */README.md       # Per-contributor notes
├── docs/
│   ├── guides/           # Runbooks (WORKFLOW, STATE_MAPPING, …)
│   ├── project/          # Deploy status, audits
│   ├── artifacts/        # Pipeline JSON outputs
│   └── scans/            # Colleague repo scans
├── sql/                  # Stage tables, merge, verify
├── src/
│   ├── convert/          # 39 state + federal_leie converters
│   ├── validate/         # Validation, audit, run manifest
│   └── pipeline.py       # End-to-end orchestrator
├── web/                  # Django search UI + API
├── tests/
├── deploy/               # Remote vesta sync scripts
└── requirements.txt
```

See [docs/guides/PROJECT_LAYOUT.md](docs/guides/PROJECT_LAYOUT.md) for architecture (canonical vs archive).

---

## Source Data

42 files in `data/raw/` covering 39 states + `LEIE.csv`. Filenames are case-sensitive.

| Contributor | States | Cleaned rows |
|-------------|--------|--------------|
| Xinzhuo Li | MD, MA, MI, MS, MT, NE | 8,575 |
| AustinGH32 | CA, NY, NC, ND, OH, NJ, PA | 44,997 |
| le-luo327 | GA–ME | 13,917 |
| AmeeBeez | AL, AK, AZ, AR, CO, CT, DE, DC, FL | 90,580 |
| FredericYan02 | SC, TN, TX, VT, WA, WV, WY | 15,242 |
| Federal LEIE | OIG | 83,464 |

Full filename table: [data/raw/README.md](data/raw/README.md). Registry: [sources/CONTRIBUTORS.yaml](sources/CONTRIBUTORS.yaml).

Colleague git clones live **outside** this repo at `../colleague-repos/` — reference only.

---

## Pipeline (Steps 0–5)

```bash
python3 -m src.pipeline [OPTIONS]
```

| Step | What it does | Output |
|------|--------------|--------|
| **0** | Preflight deps + source file SHA256 | `docs/artifacts/runs/YYYYMMDD/run_manifest_*.json` |
| **1** | Convert & clean all states | `data/processed/*`, `data/cleaned/*` |
| **2** | Validate row counts & field quality | `validation_report_*.json` — **fail-fast** |
| **3** | Rerun consistency audit | `quality_audit_*.json` — **fail-fast** |
| **4** | Load PostgreSQL stage + staging | `stage_*`, `cleaned_staging` |
| **5** | Merge to `exclusion_main` + sync verify | Strict EXCEPT check — **fail-fast** |

### CLI flags

| Flag | Description |
|------|-------------|
| `--skip-nebraska` | Skip Nebraska PDF in Steps 0–1 |
| `--skip-db` | Stop after Step 3 (no PostgreSQL) |
| `--skip-merge` | Load tables but do not merge into `exclusion_main` |
| `--states-only` | Skip federal LEIE convert/validate |

Operator runbook: [docs/guides/WORKFLOW.md](docs/guides/WORKFLOW.md).

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

---

## Testing

```bash
python3 -m pytest tests/ -v
```

198 tests cover transforms, deduplication, and record-count regression against [docs/guides/DATA_INVENTORY.md](docs/guides/DATA_INVENTORY.md).

Local validation shortcut:

```bash
bash scripts/import_local.sh --states-only
```

---

## Output Artifacts

| Artifact | Location |
|----------|----------|
| Latest run | `docs/artifacts/latest/` (symlink) |
| Run manifest | `docs/artifacts/runs/YYYYMMDD/run_manifest_*.json` |
| Validation report | `docs/artifacts/runs/YYYYMMDD/validation_report_*.json` |
| Quality audit | `docs/artifacts/runs/YYYYMMDD/quality_audit_*.json` |
| Dedup dropped | `docs/artifacts/dedup/dedup_dropped_{state}.json` |

---

## Deployment

Remote sync to vesta:

```bash
cp deploy/config.example.sh deploy/config.sh   # edit host/credentials
bash scripts/deploy_vesta.sh
```

Web search (production): http://107.181.241.82:8004/search/

Status: [docs/project/colleague_merge_status.json](docs/project/colleague_merge_status.json)

---

## Further Reading

- [docs/guides/PROJECT_LAYOUT.md](docs/guides/PROJECT_LAYOUT.md) — architecture
- [docs/guides/WORKFLOW.md](docs/guides/WORKFLOW.md) — operator runbook
- [docs/guides/DATA_INVENTORY.md](docs/guides/DATA_INVENTORY.md) — columns and quality
- [docs/guides/STATE_MAPPING.md](docs/guides/STATE_MAPPING.md) — per-state field mapping
- [sources/CONTRIBUTORS.yaml](sources/CONTRIBUTORS.yaml) — contributor registry

See [docs/project/RELEASE_STATUS.md](docs/project/RELEASE_STATUS.md) for release checklist and known limitations.

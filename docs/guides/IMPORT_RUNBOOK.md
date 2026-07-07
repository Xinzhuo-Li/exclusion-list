# Import Runbook — 39 States + LEIE

Quick reference for **adding colleague data** or **refreshing source files**.  
Detailed ETL steps: [WORKFLOW.md](WORKFLOW.md). Name rules: [NAME_HANDLING.md](NAME_HANDLING.md).

---

## Current baseline (2026-07-07)

| Layer | State Medicaid | Federal LEIE |
|-------|----------------|--------------|
| States | **39** (MD…WY, incl. DC) | OIG |
| Cleaned rows | **173,312** | **83,464** |
| Grand total | **256,776** | |
| `list_source` | `state` | `federal` |

Name audit: flagged rows for spot-check (`docs/artifacts/latest/name_audit_*.json`) — non-blocking.

Contributor registry: [sources/CONTRIBUTORS.yaml](../../sources/CONTRIBUTORS.yaml)

## Coverage policy

**39 states + DC + federal LEIE** are integrated. Twelve states remain uncovered — see [`uncovered_states.json`](../project/uncovered_states.json).

**Rule:** Do not scaffold or merge a new state until its official raw file is placed in `data/raw/` with the correct filename. No colleague cleaned CSV imports.

---

## One-command workflows

### Local validate (no database)

```bash
bash scripts/import_local.sh              # pytest + pipeline + inventory
bash scripts/import_local.sh --states-only   # 39 Medicaid states only (skip LEIE)
bash scripts/import_local.sh --quick         # skip pytest
```

Equivalent manual:

```bash
python3 -m pytest tests/ -q
python3 -m src.pipeline --skip-db
python3 scripts/inventory_data.py
```

Expected inventory: `local_state_total=173312`, `local_federal_total=83464`, `local_grand_total=256776`.

### Deploy vesta (after local PASS)

```bash
bash scripts/deploy_vesta.sh
# same as: bash deploy/sync_and_merge_noninteractive.sh
```

**Do not deploy** if validation_report shows any FAIL state.

### Clone colleague repo + copy raw files

```bash
bash scripts/merge_colleague_state.sh https://github.com/user/repo.git TX FL
bash scripts/pull_colleague_raw.sh          # pull all 4 clones; diff summary only
```

---

## Periodic refresh SOP

When a state publishes an updated exclusion list:

1. **Fetch upstream** — `bash scripts/pull_colleague_raw.sh` (or download from state website)
2. **Copy raw** — place file in `data/raw/` with **exact filename** from [data/raw/README.md](../../data/raw/README.md); never overwrite without noting SHA256 change
3. **Validate locally** — `bash scripts/import_local.sh`
4. **Review artifacts** (non-blocking name audit; blocking validation):
   - `docs/artifacts/latest/validation_report_*.json` — all states PASS
   - `docs/artifacts/latest/name_audit_*.json` — spot-check flagged names
   - `docs/artifacts/latest/run_manifest_*.json` — raw file fingerprints
5. **Deploy** (if validation PASS) — `bash scripts/deploy_vesta.sh`
6. **Refresh web metadata** on vesta:
   ```bash
   cd web && python manage.py refresh_sources
   ```
7. **Web spot-check** — search 2–3 updated states at http://107.181.241.82:8004/search/

See also [PROJECT_LAYOUT.md](PROJECT_LAYOUT.md) for canonical vs archive paths.

---

## Adding a **new state** (full checklist)

1. **Raw file** → `data/raw/` (update `data/raw/README.md`)
2. **Converter** — scaffold then edit:
   ```bash
   python3 scripts/scaffold_state.py TX texas Texas.xlsx
   # or: Texas.pdf --entity-column
   # or: Texas.csv --combined-name
   ```
3. **Names** — use `resolve_name_fields()` only ([NAME_HANDLING.md](NAME_HANDLING.md))
4. **Register** in:
   - `src/convert/run_all.py`
   - `src/config.py` (`ALL_SOURCE_STATES`)
   - `sql/01_create_stage_tables.sql`
   - `src/load/load_to_postgres.py`
   - `sql/03_merge_to_main.sql`
   - `src/validate/check_import.py` (`STATE_EXPECTATIONS`)
   - `web/exclusions/queries.py` (`STATE_NAMES`)
   - `sources/CONTRIBUTORS.yaml`
5. **Document** → `docs/guides/FIELD_SEMANTICS.md`, `STATE_MAPPING.md`, `DATA_INVENTORY.md`
6. **Validate** → `bash scripts/import_local.sh --states-only`
7. **Deploy** → `bash scripts/deploy_vesta.sh`

---

## Pipeline steps (automatic)

| Step | What |
|------|------|
| 0 | Preflight deps + `run_manifest` — raw file SHA256 |
| 1 | `run_all` — convert → `data/processed/`, `data/cleaned/` |
| 2 | `check_import` — row counts, NPI/date rates |
| 3 | `name_audit` — name field spot-check flags |
| 4 | `quality_audit` — rerun consistency |
| 5–6 | load PostgreSQL + merge (`exclusion_main`) |

Flags: `--skip-db`, `--states-only`, `--skip-nebraska`, `--skip-merge`

---

## Changelog summary (recent merges)

### AmeeBeez 9 states (AL–FL excl. CA) + Frederic 7 states (SC–WY)

- Raw-only ETL into canonical pipeline (2026-07)
- TX requires `xlrd` for `.xls`

### Austin 7 states (CA, NY, NC, ND, OH, NJ, PA)

- Unified OIG schema + `list_source=state`
- PA: `reindate` only for Reinstated; `state` from CAO
- OH: `excltype` from Status

### Le Luo 10 states (GA…ME)

- PDF states: HI, ID, ME; `resolve_name_fields` for IL, IN, KS, ID

### Federal LEIE

- `data/raw/LEIE.csv` → `federal_oig.csv` when **not** using `--states-only`
- Merge via `list_source=federal` in `sql/03_merge_to_main.sql`

---

## Scripts index

| Script | Purpose |
|--------|---------|
| `scripts/import_local.sh` | **Main** local validate entry |
| `scripts/deploy_vesta.sh` | Deploy to production server |
| `scripts/pull_colleague_raw.sh` | Pull 4 colleague clones (no auto-copy to data/raw) |
| `scripts/scaffold_state.py` | New `src/convert/{state}.py` template |
| `scripts/inventory_data.py` | Row counts → `docs/artifacts/runs/YYYYMMDD/inventory_*.json` |
| `scripts/merge_colleague_state.sh` | Clone + integrate colleague repo |
| `src/pipeline.py` | Full ETL orchestrator |
| `deploy/audit_vesta.sh` | Remote DB audit (39 states + LEIE) |
| `deploy/sync_and_merge_noninteractive.sh` | Rsync + DB reload + merge |

---

## Reports to review after each import

| File | Purpose |
|------|---------|
| `docs/artifacts/latest/validation_report_*.json` | Row counts PASS/FAIL |
| `docs/artifacts/latest/name_audit_*.json` | Name fields to spot-check |
| `docs/artifacts/dedup/dedup_dropped_{state}.json` | Exact duplicates removed |
| `docs/artifacts/latest/run_manifest_*.json` | Raw file fingerprints |
| `docs/artifacts/latest/inventory_*.json` | Per-state row summary |

---

## Troubleshooting

| Problem | What to do |
|---------|------------|
| Texas convert fails (`xlrd`) | `pip install -r requirements.txt`; see [pipeline_incident_20260707_xlrd.md](../project/pipeline_incident_20260707_xlrd.md) |
| PDF state fails | Install `pdfplumber`; verify NE/HI/ID/ME/WY raw files exist |
| validation FAIL | Read `docs/artifacts/latest/validation_report_*.json` for failing state |
| vesta count mismatch | Run `deploy/audit_vesta.sh`; compare with `docs/project/vesta_audit_YYYYMMDD.json` |
| Local DB merge untested | `bash scripts/check_postgres.sh` then `bash scripts/import_with_db.sh` |

## Danger — partial load + merge

**Never** load a subset of states into `cleaned_staging` and then run merge.

`load_cleaned_data()` TRUNCATEs staging; merge deletes **all 39 state slices** from `exclusion_main` and re-inserts only what is in staging. A partial load (e.g. TX only) **removes the other 38 states**.

Protection: [`src/load/merge_guard.py`](../../src/load/merge_guard.py) blocks partial load by default and validates 40 sources before merge. See [MERGE_SEMANTICS.md](MERGE_SEMANTICS.md).

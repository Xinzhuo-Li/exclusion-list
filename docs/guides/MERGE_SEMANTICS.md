# Merge semantics — exclusion_main vs cleaned_staging

How data flows into the production table and what sync verification means.

## Flow

```
data/cleaned/*_oig.csv + federal_oig.csv
    → load_cleaned_data() TRUNCATE + INSERT cleaned_staging
    → sql/03_merge_to_main.sql DELETE managed slices + INSERT from staging
    → exclusion_main
```

Merge is **slice replacement**, not row-by-row UPSERT:

| `list_source` | DELETE scope | INSERT from staging |
|---------------|--------------|-------------------|
| `state` | All rows where `source_state IN (39 active states)` | `WHERE list_source = 'state'` |
| `federal` | All rows where `list_source = 'federal'` | `WHERE list_source = 'federal'` |

## Sync columns (20 business fields)

Verification compares these columns only — see `SYNC_COLUMNS` in [`src/pipeline.py`](../../src/pipeline.py) and [`sql/04_verify_main_sync.sql`](../../sql/04_verify_main_sync.sql):

`lastname, firstname, midname, busname, general, specialty, upin, npi, dob, address, city, state, zip_code, excltype, excldate, reindate, waiverdate, waiverstate, list_source, source_state`

**Not compared:** `id`, `loaded_at`

## `loaded_at` behavior

- Set at **load time** when rows are inserted into `cleaned_staging` / `exclusion_main`
- Refreshed on every full merge (expected)
- **Not** used for deduplication or sync equality
- Web/API search uses exclusion business fields, not `loaded_at`

## Partial load danger

`load_cleaned_data()` **TRUNCATE**s `cleaned_staging` then inserts selected CSVs.

If you load only one state (e.g. `states=['tx']`) and run merge:

1. Staging contains TX (+ federal if present) only
2. Merge **deletes all 39 state slices** from `exclusion_main`
3. Only TX rows are re-inserted → **38 states lost**

**Protection (2026-07):**

- [`src/load/merge_guard.py`](../../src/load/merge_guard.py) — refuses partial load by default; requires 40 `source_state` values before merge
- [`sql/05_assert_coverage.sql`](../../sql/05_assert_coverage.sql) — deploy post-check for row/source counts

**Never** run merge after partial load unless you intentionally understand the data loss.

## Safe commands

```bash
# Local CSV + validate only (no DB)
bash scripts/import_local.sh

# Full local load + merge (requires PostgreSQL)
bash scripts/check_postgres.sh
bash scripts/import_with_db.sh

# Production (configure deploy/config.sh first)
bash deploy/sync_and_merge_noninteractive.sh
```

## Dev-only partial load

```bash
ALLOW_PARTIAL_LOAD=1 python3 -m src.load.load_to_postgres -- ...  # if CLI added
# Do NOT run merge afterward — staging guard will fail
```

See also [`IMPORT_RUNBOOK.md`](IMPORT_RUNBOOK.md) Danger section.

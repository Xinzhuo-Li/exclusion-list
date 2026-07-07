# EMRTS Project Summary (2026-07-07)

One-page update supplementing the June 2026 course report (originally **6 states**).

## Project goal

Merge US Medicaid provider exclusion lists into a unified OIG LEIE schema, load into PostgreSQL `exclusion_main`, and expose a searchable web UI.

## Current scale (vs original 6-state report)

| Metric | June 2026 report | July 2026 production |
|--------|------------------|----------------------|
| States | 6 (MD–NE) | **39** + DC |
| Federal LEIE | Not included | **83,464** rows |
| Total records | ~8,575 | **256,776** |
| Contributors | 1 | **5** + federal (Le Luo LEIE) |

## Architecture (canonical path)

```
data/raw/ → src/convert/ → data/cleaned/ → pipeline → PostgreSQL exclusion_main → web search
```

See [`PROJECT_LAYOUT.md`](../guides/PROJECT_LAYOUT.md) for contributor mapping and archive policy.

## Production

- **URL:** http://107.181.241.82:8004/search/
- **Search:** Name (first/middle/last/business) + NPI
- **Deploy:** `bash scripts/deploy_vesta.sh`

## Validation

- pytest + `import_local.sh` before every deploy
- Merge guards prevent partial-state data loss (`merge_guard.py`)
- Audit: [`vesta_audit_20260707.json`](vesta_audit_20260707.json)

## Original report files (historical)

Located in `docs/project/`: `EMRTS_Project_report_Medicaid_Exclusion_List_2026.06.28_Xinzhuo_Li.*` — describes early 6-state milestone only.

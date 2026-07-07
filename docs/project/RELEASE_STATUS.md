# Release Status — 39 States + LEIE (2026-07-07)

Production-ready snapshot for GitHub and team onboarding.

## Production

| Item | Value |
|------|-------|
| Web search | http://107.181.241.82:8004/search/ |
| Records | **256,776** (173,312 state + 83,464 OIG) |
| Last deploy | 2026-07-07 (`deploy_vesta.sh`) |
| Repository | https://github.com/Xinzhuo-Li/medicaid-exclusion-list |

## Completed

| Area | Status | Evidence |
|------|--------|----------|
| 39-state ETL | Done | 173,312 cleaned rows; 39 converters in `src/convert/` |
| Federal LEIE | Done | `data/raw/LEIE.csv` → 83,464 rows; `list_source=federal` |
| vesta DB | Deployed | [`vesta_audit_20260707.json`](vesta_audit_20260707.json) |
| Validation | PASS | pytest 237+; `import_local.sh`; OIG validation PASS |
| Web search | Simplified | Name + NPI only; [`web_spotcheck_20260707.md`](web_spotcheck_20260707.md) |
| Framework | Done | `sources/CONTRIBUTORS.yaml`; docs/guides; `PROJECT_LAYOUT.md` |
| Merge guards | Done | `merge_guard.py`; `MERGE_SEMANTICS.md`; `05_assert_coverage.sql` |
| Deploy | Done | `scripts/deploy_vesta.sh`; `sync_and_merge_noninteractive.sh` |

## Not done / non-blocking

| Item | Priority | Notes |
|------|----------|-------|
| 12 uncovered states | Passive | See [`uncovered_states.json`](uncovered_states.json) — integrate only when raw exists |
| Contributor README review | Optional | Each contributor confirms `sources/{id}/README.md` |
| EMRTS course report (2026.06.28) | Historical | Original PDF describes 6-state era; see [`EMRTS_REPORT_SUMMARY_20260707.md`](EMRTS_REPORT_SUMMARY_20260707.md) |
| Django model migrations | Low | `makemigrations` warning on vesta; non-blocking for search |

## Known limitations (not bugs)

- `quality_audit` rerun comparison covers original MD–NE six states only; other states rely on `check_import`
- Tennessee (TN) has ~21 source rows — small list, not a pipeline error
- `name_audit` flags ~1,500+ rows (many in FL) — non-blocking spot-check list
- Local Mac PostgreSQL often unavailable; DB merge acceptance uses vesta deploy
- `loaded_at` is not part of sync equality (see [`MERGE_SEMANTICS.md`](../guides/MERGE_SEMANTICS.md))

## Key paths

| Purpose | Path |
|---------|------|
| Merge status | [`colleague_merge_status.json`](colleague_merge_status.json) |
| Uncovered states | [`uncovered_states.json`](uncovered_states.json) |
| Operator runbook | [`IMPORT_RUNBOOK.md`](../guides/IMPORT_RUNBOOK.md) |
| Architecture | [`PROJECT_LAYOUT.md`](../guides/PROJECT_LAYOUT.md) |
| Contributor registry | [`sources/CONTRIBUTORS.yaml`](../../sources/CONTRIBUTORS.yaml) |

## Refresh SOP

```bash
bash scripts/pull_colleague_raw.sh    # optional: update colleague clones
# copy new raw → data/raw/ (exact filenames)
bash scripts/import_local.sh          # validate
bash scripts/deploy_vesta.sh          # production sync
```

## GitHub sync

| Item | Value |
|------|-------|
| Status | **Committed locally** — push pending |
| Branch | `main` (297 files; see `git log -1`) |
| Remote | https://github.com/Xinzhuo-Li/medicaid-exclusion-list |

```bash
git push -u origin main
```

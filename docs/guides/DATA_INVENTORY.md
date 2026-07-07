# Data Inventory — 39 Medicaid States + Federal LEIE

**Baseline (2026-07-07):**

| Layer | Count | Notes |
|-------|------:|-------|
| State Medicaid cleaned | **173,312** | `list_source = state` |
| Federal LEIE cleaned | **83,464** | `list_source = federal`, `source_state = OIG` |
| **Grand total** | **256,776** | |

See [FIELD_SEMANTICS.md](FIELD_SEMANTICS.md) for unified field meanings.  
Per-state raw filenames: [data/raw/README.md](../../data/raw/README.md).  
Contributor mapping: [sources/CONTRIBUTORS.yaml](../../sources/CONTRIBUTORS.yaml).

## Generated outputs (local only, gitignored)

Running `python3 -m src.pipeline --skip-db` writes:

| Path | Pattern |
|------|---------|
| `data/processed/` | `{state}_raw.csv` — state-native columns |
| `data/cleaned/` | `{state}_oig.csv` — OIG LEIE schema |
| `data/cleaned/federal_oig.csv` | Federal LEIE |

Pipeline validation baselines live in `src/validate/check_import.py` → `STATE_EXPECTATIONS`.

## Record counts by contributor (cleaned, 2026-07-07)

| Contributor | States | Cleaned records |
|-------------|--------|----------------:|
| Xinzhuo Li | MD, MA, MI, MS, MT, NE | 8,575 |
| AustinGH32 | CA, NY, NC, ND, OH, NJ, PA | 44,997 |
| le-luo327 | GA, HI, ID, IL, IN, IA, KS, KY, LA, ME | 13,917 |
| AmeeBeez | AL, AK, AZ, AR, CO, CT, DE, DC, FL | 90,580 |
| FredericYan02 | SC, TN, TX, VT, WA, WV, WY | 15,242 |
| le-luo327 (federal) | OIG LEIE | 83,464 |
| **Total** | **39 + DC + OIG** | **256,776** |

## Notable per-state counts

| State | Cleaned | Notes |
|-------|--------:|-------|
| FL | 83,114 | Largest state list |
| TX | 13,324 | Requires `xlrd` for `.xls` source |
| CA | 23,094 | CSV source |
| MI | 4,921 | Multi-date expansion (3,982 source rows) |
| TN | 21 | Small official list |
| DC | 93 | District of Columbia |

Full per-state processed/cleaned counts: run `bash scripts/import_local.sh --quick` and inspect the validation report under local `docs/artifacts/runs/YYYYMMDD/`.

## Data quality notes

- **NPI coverage** varies by state; see `STATE_EXPECTATIONS` in `src/validate/check_import.py`
- **Date format**: all `EXCLDATE` values converted to `YYYYMMDD`
- **Name fields**: preserved in full (`TEXT`); no OIG length truncation at clean time
- **PDF states**: NE, HI, ID, ME, WY — parsed via `pdfplumber` (no OCR)
- **Federal LEIE**: `data/raw/LEIE.csv` → `federal_oig.csv`
- **Dedup**: only exact duplicates (all identity fields identical); cross-state NPI duplicates retained

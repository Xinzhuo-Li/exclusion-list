# Source Files (`data/raw/`)

Place state Medicaid exclusion/sanction source files here. **Filenames are case-sensitive** and must match exactly.

**Canonical rule:** This folder is the only raw input for `python3 -m src.pipeline`. Colleague repo clones under `../colleague-repos/` are reference — copy files here before running ETL.

Contributor registry: [sources/CONTRIBUTORS.yaml](../../sources/CONTRIBUTORS.yaml)

---

## Xinzhuo Li — 6 states

| State | Code | Required filename | Format |
|-------|------|-------------------|--------|
| Maryland | MD | `Maryland.xlsx` | Excel |
| Massachusetts | MA | `Massachusetts.xlsx` | Excel |
| Michigan | MI | `Michigan.xlsx` | Excel |
| Mississippi | MS | `Mississippi.xlsx` | Excel |
| Montana | MT | `Montana.xlsx` | Excel |
| Nebraska | NE | `Nebraska.pdf` | PDF (table extraction) |

## AustinGH32 — 7 states

| State | Code | Required filename | Format |
|-------|------|-------------------|--------|
| California | CA | `California.csv` | CSV |
| New York | NY | `NewYork.xlsx` | Excel |
| North Carolina | NC | `NorthCarolina.xlsx` | Excel |
| North Dakota | ND | `NorthDakota.xlsx` | Excel |
| Ohio | OH | `Ohio.xlsx` | Excel (2 sheets) |
| New Jersey | NJ | `NewJersey.csv` | CSV |
| Pennsylvania | PA | `Pennsylvania.csv` | CSV |

## le-luo327 — 10 states

| State | Code | Required filename | Format |
|-------|------|-------------------|--------|
| Georgia | GA | `Georgia.xlsx` | Excel |
| Hawaii | HI | `Hawaii.pdf` | PDF |
| Idaho | ID | `Idaho.pdf` | PDF |
| Illinois | IL | `Illinois.xlsx` | Excel |
| Indiana | IN | `Indiana.xlsx` | Excel |
| Iowa | IA | `Iowa.xlsx` | Excel |
| Kansas | KS | `Kansas.xlsx` | Excel |
| Kentucky | KY | `Kentucky.xlsx` | Excel |
| Louisiana | LA | `Louisiana.xlsx` | Excel |
| Maine | ME | `Maine.pdf` | PDF |

## AmeeBeez — 9 states (CA skipped)

| State | Code | Required filename | Format |
|-------|------|-------------------|--------|
| Alabama | AL | `Alabama.xlsx` | Excel |
| Alaska | AK | `Alaska.csv` | CSV |
| Arizona | AZ | `Arizona.xlsx` | Excel |
| Arkansas | AR | `Arkansas.csv` | CSV |
| Colorado | CO | `Colorado.xlsx` | Excel |
| Connecticut | CT | `Connecticut.xlsx` | Excel |
| Delaware | DE | `Delaware.csv` | CSV |
| District of Columbia | DC | `DistrictOfColumbia.csv` | CSV |
| Florida | FL | `Florida.csv` | CSV |

## FredericYan02 — 7 states

| State | Code | Required filename | Format |
|-------|------|-------------------|--------|
| South Carolina | SC | `SouthCarolina.xlsx` | Excel |
| Tennessee | TN | `Tennessee.xlsx` | Excel |
| Texas | TX | `Texas.xls` | Excel (.xls — requires xlrd) |
| Vermont | VT | `Vermont.xlsx` | Excel |
| Washington | WA | `Washington.xlsx` | Excel |
| West Virginia | WV | `WestVirginia.csv` | CSV |
| Wyoming | WY | `Wyoming.pdf` | PDF |

## Federal LEIE

| Source | Required filename | Format |
|--------|-------------------|--------|
| HHS OIG LEIE | `LEIE.csv` | CSV |

Download from [OIG LEIE](https://oig.hhs.gov/exclusions/exclusions_list.asp) and save as **`data/raw/LEIE.csv`**.  
If you receive a file named `UPDATED.csv` (or similar), rename or copy it to `LEIE.csv` — do not keep a duplicate at the repo root.

When `LEIE.csv` is present, the pipeline also builds `data/cleaned/federal_oig.csv` (`list_source=federal`, merged into `exclusion_main` via `list_source=federal`).

## Optional reference

| File | Purpose |
|------|---------|
| `数据结构.pdf` | OIG LEIE target schema reference (not used by ETL code) |

---

## After updating source files

1. Run: `python3 -m src.pipeline --skip-db` (or full pipeline with PostgreSQL).
2. Check `docs/artifacts/runs/YYYYMMDD/run_manifest_*.json` for SHA256 fingerprints.
3. If record counts change intentionally, update `STATE_EXPECTATIONS` in `src/validate/check_import.py` and counts in `docs/guides/DATA_INVENTORY.md`.

See [docs/guides/WORKFLOW.md](../guides/WORKFLOW.md) for the full step-by-step guide.

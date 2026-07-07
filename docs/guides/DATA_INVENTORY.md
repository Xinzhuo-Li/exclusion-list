# Data Inventory — Twenty-Three Medicaid States + Federal LEIE

**State Medicaid cleaned (2026-07-03): 67,488** — all `list_source = state`.  
**Federal LEIE cleaned: 83,464** — `list_source = federal`, `source_state = OIG`.  
**Combined: 150,953**  
See [FIELD_SEMANTICS.md](FIELD_SEMANTICS.md) for unified field meanings.

## Source Files

### Original six states

| State | Code | File | Format | Location |
|-------|------|------|--------|----------|
| Maryland | MD | Maryland.xlsx | Excel | `data/raw/Maryland.xlsx` |
| Massachusetts | MA | Massachusetts.xlsx | Excel | `data/raw/Massachusetts.xlsx` |
| Michigan | MI | Michigan.xlsx | Excel | `data/raw/Michigan.xlsx` |
| Mississippi | MS | Mississippi.xlsx | Excel | `data/raw/Mississippi.xlsx` |
| Montana | MT | Montana.xlsx | Excel | `data/raw/Montana.xlsx` |
| Nebraska | NE | Nebraska.pdf | PDF (table) | `data/raw/Nebraska.pdf` |

### Austin colleague states (contributor: AustinGH32)

| State | Code | File | Format | Location |
|-------|------|------|--------|----------|
| California | CA | California.csv | CSV | `data/raw/California.csv` |
| New York | NY | NewYork.xlsx | Excel | `data/raw/NewYork.xlsx` |
| North Carolina | NC | NorthCarolina.xlsx | Excel | `data/raw/NorthCarolina.xlsx` |
| North Dakota | ND | NorthDakota.xlsx | Excel | `data/raw/NorthDakota.xlsx` |
| Ohio | OH | Ohio.xlsx | Excel (2 sheets) | `data/raw/Ohio.xlsx` |
| New Jersey | NJ | NewJersey.csv | CSV | `data/raw/NewJersey.csv` |
| Pennsylvania | PA | Pennsylvania.csv | CSV | `data/raw/Pennsylvania.csv` |

### Le Luo colleague states (contributor: le-luo327)

| State | Code | File | Format | Location |
|-------|------|------|--------|----------|
| Georgia | GA | Georgia.xlsx | Excel | `data/raw/Georgia.xlsx` |
| Hawaii | HI | Hawaii.pdf | PDF | `data/raw/Hawaii.pdf` |
| Idaho | ID | Idaho.pdf | PDF | `data/raw/Idaho.pdf` |
| Illinois | IL | Illinois.xlsx | Excel | `data/raw/Illinois.xlsx` |
| Indiana | IN | Indiana.xlsx | Excel | `data/raw/Indiana.xlsx` |
| Iowa | IA | Iowa.xlsx | Excel | `data/raw/Iowa.xlsx` |
| Kansas | KS | Kansas.xlsx | Excel | `data/raw/Kansas.xlsx` |
| Kentucky | KY | Kentucky.xlsx | Excel | `data/raw/Kentucky.xlsx` |
| Louisiana | LA | Louisiana.xlsx | Excel | `data/raw/Louisiana.xlsx` |
| Maine | ME | Maine.pdf | PDF | `data/raw/Maine.pdf` |

### Federal LEIE (contributor: le-luo327)

| Source | File | Format | Location |
|--------|------|--------|----------|
| HHS OIG LEIE | LEIE.csv | CSV | `data/raw/LEIE.csv` |

## Processed Output Files

| State | Processed CSV | Cleaned CSV |
|-------|---------------|-------------|
| MD | `data/processed/md_raw.csv` | `data/cleaned/md_oig.csv` |
| MA | `data/processed/ma_raw.csv` | `data/cleaned/ma_oig.csv` |
| MI | `data/processed/mi_raw.csv` | `data/cleaned/mi_oig.csv` |
| MS | `data/processed/ms_raw.csv` | `data/cleaned/ms_oig.csv` |
| MT | `data/processed/mt_raw.csv` | `data/cleaned/mt_oig.csv` |
| NE | `data/processed/ne_raw.csv` | `data/cleaned/ne_oig.csv` |
| NC | `data/processed/nc_raw.csv` | `data/cleaned/nc_oig.csv` |
| ND | `data/processed/nd_raw.csv` | `data/cleaned/nd_oig.csv` |
| OH | `data/processed/oh_raw.csv` | `data/cleaned/oh_oig.csv` |
| NJ | `data/processed/nj_raw.csv` | `data/cleaned/nj_oig.csv` |
| NY | `data/processed/ny_raw.csv` | `data/cleaned/ny_oig.csv` |
| PA | `data/processed/pa_raw.csv` | `data/cleaned/pa_oig.csv` |
| CA | `data/processed/ca_raw.csv` | `data/cleaned/ca_oig.csv` |
| GA | `data/processed/ga_raw.csv` | `data/cleaned/ga_oig.csv` |
| HI | `data/processed/hi_raw.csv` | `data/cleaned/hi_oig.csv` |
| ID | `data/processed/id_raw.csv` | `data/cleaned/id_oig.csv` |
| IL | `data/processed/il_raw.csv` | `data/cleaned/il_oig.csv` |
| IN | `data/processed/in_raw.csv` | `data/cleaned/in_oig.csv` |
| IA | `data/processed/ia_raw.csv` | `data/cleaned/ia_oig.csv` |
| KS | `data/processed/ks_raw.csv` | `data/cleaned/ks_oig.csv` |
| KY | `data/processed/ky_raw.csv` | `data/cleaned/ky_oig.csv` |
| LA | `data/processed/la_raw.csv` | `data/cleaned/la_oig.csv` |
| ME | `data/processed/me_raw.csv` | `data/cleaned/me_oig.csv` |
| Federal | — | `data/cleaned/federal_oig.csv` |

## Record Counts (Latest Run — 2026-07-03)

| State | Raw Rows | Cleaned Records | Notes |
|-------|----------|-----------------|-------|
| MD | 1,605 | 1,603 | |
| MA | 294 | 294 | |
| MI | 3,982 | 4,921 | Multi-date expansion |
| MS | 194 | 193 | |
| MT | 174 | 174 | |
| NE | 1,391 | 1,390 | |
| NC | 176 | 166 | |
| ND | 195 | 195 | |
| OH | 2,017 | 2,017 | |
| NJ | 4,022 | 4,021 | |
| NY | 8,931 | 8,913 | |
| PA | 6,659 | 6,591 | |
| CA | 23,120 | 23,094 | |
| GA | 1,370 | 1,346 | Le Luo |
| HI | 213 | 213 | PDF |
| ID | 171 | 171 | PDF |
| IL | 3,229 | 3,203 | Address mapped |
| IN | 151 | 151 | |
| IA | 1,272 | 1,271 | |
| KS | 199 | 198 | |
| KY | 397 | 396 | |
| LA | 5,880 | 5,859 | DOB mapped |
| ME | 1,108 | 1,108 | PDF |
| **State total** | **67,760** | **67,488** | |
| **Federal LEIE** | **83,464** | **83,464** | `list_source=federal` |
| **Grand total** | | **150,953** | |

Dedup only removes exact duplicates (all identity fields identical). Michigan dual sanction dates produce two records per source row. Name fields are not truncated.

## Data Quality Notes

- **NPI coverage** varies by state; see `src/validate/check_import.py` `STATE_EXPECTATIONS` for minimum rates per state
- **Date format**: All `EXCLDATE` values converted to `YYYYMMDD`
- **Name fields**: Preserved in full; OIG reference length limits are not applied during cleaning
- **Nebraska PDF**: Parsed via pdfplumber table extraction; no OCR needed
- **Federal OIG (LEIE)**: `data/raw/LEIE.csv` → `federal_oig.csv` (`list_source=federal`, 83,464 rows)

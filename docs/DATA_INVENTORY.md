# Data Inventory — Six Assigned States

## Source Files

| State | Code | File | Format | Location |
|-------|------|------|--------|----------|
| Maryland | MD | Maryland.xlsx | Excel | `data/raw/Maryland.xlsx` |
| Massachusetts | MA | Massachusetts.xlsx | Excel | `data/raw/Massachusetts.xlsx` |
| Michigan | MI | Michigan.xlsx | Excel | `data/raw/Michigan.xlsx` |
| Mississippi | MS | Mississippi.xlsx | Excel | `data/raw/Mississippi.xlsx` |
| Montana | MT | Montana.xlsx | Excel | `data/raw/Montana.xlsx` |
| Nebraska | NE | Nebraska.pdf | PDF (table) | `data/raw/Nebraska.pdf` |

## Processed Output Files

| State | Processed CSV | Cleaned CSV |
|-------|---------------|-------------|
| MD | `data/processed/md_raw.csv` | `data/cleaned/md_oig.csv` |
| MA | `data/processed/ma_raw.csv` | `data/cleaned/ma_oig.csv` |
| MI | `data/processed/mi_raw.csv` | `data/cleaned/mi_oig.csv` |
| MS | `data/processed/ms_raw.csv` | `data/cleaned/ms_oig.csv` |
| MT | `data/processed/mt_raw.csv` | `data/cleaned/mt_oig.csv` |
| NE | `data/processed/ne_raw.csv` | `data/cleaned/ne_oig.csv` |

## Source Column Inventory

### Maryland (9 columns)
- LAST NAME/ORGANIZATION
- FIRST NAME
- TYPE OF ENTITY/PROFESSION
- SANCTION TYPE
- NPI
- LICENSE NO
- TERMINATION/SANCTION DATE
- ADDRESS
- CITY/STATE/ZIP

### Massachusetts (6 columns)
- Provider Name
- Provider Type
- National Provider Identifier (NPI)
- Unique ID
- Suspension/Exclusion Reason
- Suspension/Exclusion Effective Date

### Michigan (13 columns)
- Entity Name, Last Name, First Name, Middle Name
- Provider Category, NPI#, City, License#
- Sanction Date1, Sanction Source
- Sanction Date2, Sanction Source.1
- Reason

### Mississippi (24 columns)
- Provider Entity (Org/Ind), Role
- Organization Name, First/Last/MI/Suffix Name
- Address Line 1/2, City, State, Zipcode
- NPI, Medicaid ID, Date of Birth
- Provider Type, Provider Speciality
- Termination Effective/End Date, Exclusion Period
- Termination Reason, Sanction Type, Additional Notes

### Montana (5 columns)
- Terminated/Excluded Provider(s)
- Healthcare Profession
- NPI
- Effective Date
- Sanction Type (unnamed column E)

### Nebraska (9 columns, PDF table)
- Date Added to NMEP
- Provider Name
- Organization Name
- Provider NPI
- Effective Date
- Provider Type Code
- Reason For Action Code
- Sanction Code
- Sanction Type Code

## Record Counts (Latest Run)

| State | Raw Rows | Cleaned Records | Notes |
|-------|----------|-----------------|-------|
| MD | 1,605 | 1,603 | 6 legend rows filtered; 2 exact duplicates removed |
| MA | 294 | 294 | 0 removed |
| MI | 3,982 | 4,921 | Multi-date cells expanded; 6 exact duplicates removed |
| MS | 194 | 193 | 1 empty source row skipped; indefinite REINDATE cleared |
| MT | 174 | 174 | a.k.a. alias names parsed |
| NE | 1,391 | 1,390 | 1 exact duplicate removed |
| **Total** | **7,640** | **8,575** | |

Dedup only removes exact duplicates (all identity fields identical). Michigan dual sanction dates produce two records per source row. Name fields are not truncated.

## Data Quality Notes

- **NPI coverage** varies by state: MA (~81%), MI (~29%), MD (~17%), MT (~25%), NE (~20%), MS (~75%)
- **Date format**: All `EXCLDATE` values converted to `YYYYMMDD`
- **Name fields**: Preserved in full; OIG reference length limits are not applied during cleaning
- **Nebraska PDF**: Parsed via pdfplumber table extraction; no OCR needed

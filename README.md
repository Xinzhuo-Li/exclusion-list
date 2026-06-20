# Six-State Medical Exclusion List ETL

ETL pipeline for merging Maryland, Massachusetts, Michigan, Mississippi, Montana, and Nebraska Medicaid exclusion lists into a PostgreSQL database using the OIG LEIE schema.

## Project Structure

```
州exclusion list/
├── data/
│   ├── raw/           # Original source files
│   ├── processed/     # Converted CSV (state-native columns)
│   └── cleaned/       # OIG-mapped CSV output
├── sql/
│   ├── 01_create_stage_tables.sql
│   ├── 02_create_main_table.sql
│   └── 03_merge_to_main.sql
├── src/
│   ├── clean/         # Shared cleaning utilities
│   ├── convert/       # Per-state converters
│   ├── load/          # PostgreSQL loader
│   ├── validate/      # Import validation
│   └── pipeline.py    # End-to-end runner
└── docs/
    ├── DATA_INVENTORY.md
    └── STATE_MAPPING.md
```

## Setup

```bash
cd "州exclusion list"
pip3 install -r requirements.txt
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

## PostgreSQL Setup (Linux Server)

```bash
# Create database
sudo -u postgres psql -c "CREATE DATABASE exclusion_list;"

# Or connect remotely and run:
psql -h <host> -U <user> -d exclusion_list -f sql/01_create_stage_tables.sql
psql -h <host> -U <user> -d exclusion_list -f sql/02_create_main_table.sql
```

## Run Pipeline

### Full pipeline (convert → validate → load → merge)

```bash
python3 -m src.pipeline
```

### Convert and clean only (no database)

```bash
python3 -m src.pipeline --skip-db
```

### Individual steps

```bash
# Step 1-2: Convert all states
python3 -m src.convert.run_all

# Step 4: Validate outputs
python3 -m src.validate.check_import

# Step 3: Load into PostgreSQL
python3 -m src.load.load_to_postgres

# Step 5: Merge into main table
psql -h <host> -U <user> -d exclusion_list -f sql/03_merge_to_main.sql
```

## State Summary

| State | Source File | Processed Rows | Cleaned Records |
|-------|-------------|----------------|-----------------|
| MD | Maryland.xlsx | 1,605 | 1,603 |
| MA | Massachusetts.xlsx | 294 | 294 |
| MI | Michigan.xlsx | 3,982 | 4,921 |
| MS | Mississippi.xlsx | 194 | 193 |
| MT | Montana.xlsx | 174 | 174 |
| NE | Nebraska.pdf | 1,391 | 1,390 |

**Total cleaned records: 8,575**

## Target Schema (OIG LEIE)

Fields from `数据结构.pdf`:

`LASTNAME, FIRSTNAME, MIDNAME, BUSNAME, GENERAL, SPECIALTY, UPIN, NPI, DOB, ADDRESS, CITY, STATE, ZIP CODE, EXCLTYPE, EXCLDATE, REINDATE, WAIVERDATE, WAIVERSTATE`

Plus `source_state` for tracking which state file each record came from.

## Deployment to Linux Server

```bash
# Copy project to server
scp -r "州exclusion list" user@server:/path/to/project/

# SSH into server
ssh user@server
cd /path/to/project/州exclusion list

# Install dependencies and run
pip3 install -r requirements.txt
python3 -m src.pipeline --skip-db   # Generate CSVs locally first
python3 -m src.pipeline               # Full load after DB is configured
```

## Notes

- Nebraska PDF is parsed via `pdfplumber` table extraction (no OCR required).
- Excel dates are converted to `YYYYMMDD` format.
- Mississippi `Termination End Date` value `401768` (indefinite) is mapped to empty `REINDATE`.
- Validation reports are written to `docs/validation_report_*.json`.

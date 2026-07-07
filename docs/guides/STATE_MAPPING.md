# State → OIG LEIE Field Mapping

Target schema from `数据结构.pdf` (18 OIG LEIE fields + `source_state`).

## OIG Field Definitions

| OIG Field | Max Length | Description |
|-----------|------------|-------------|
| LASTNAME | 20 | Individual last name |
| FIRSTNAME | 15 | Individual first name |
| MIDNAME | 15 | Individual middle name |
| BUSNAME | 30 | Business/organization name |
| GENERAL | 20 | Provider type / profession |
| SPECIALTY | 20 | Medical specialty |
| UPIN | 6 | Legacy UPIN (unused) |
| NPI | 10 | National Provider Identifier |
| DOB | 8 | Date of birth (YYYYMMDD) |
| ADDRESS | 30 | Street address |
| CITY | 20 | City |
| STATE | 2 | 2-letter state code |
| ZIP CODE | 5 | 5-digit ZIP |
| EXCLTYPE | 9 | Exclusion/sanction type |
| EXCLDATE | 8 | Exclusion effective date (YYYYMMDD) |
| REINDATE | 8 | Reinstatement date (YYYYMMDD) |
| WAIVERDATE | 8 | Waiver date (unused) |
| WAIVERSTATE | 2 | Waiver state (unused) |

## Per-State Mapping

### Maryland (MD)

| OIG Field | Source Column | Transform |
|-----------|---------------|-----------|
| LASTNAME | LAST NAME/ORGANIZATION | If individual (has FIRST NAME) |
| FIRSTNAME | FIRST NAME | Direct |
| BUSNAME | LAST NAME/ORGANIZATION | If organization (Business Entity) |
| GENERAL | TYPE OF ENTITY/PROFESSION | Preserve full length (OIG ref max 20) |
| NPI | NPI | 10-digit validation |
| ADDRESS | ADDRESS | Preserve full length (OIG ref max 30) |
| CITY | CITY/STATE/ZIP | Parsed via regex |
| STATE | CITY/STATE/ZIP | Parsed; default MD |
| ZIP CODE | CITY/STATE/ZIP | First 5 digits |
| EXCLTYPE | SANCTION TYPE | Normalized (MDH, LB, etc.) |
| EXCLDATE | TERMINATION/SANCTION DATE | Excel serial → YYYYMMDD |

### Massachusetts (MA)

| OIG Field | Source Column | Transform |
|-----------|---------------|-----------|
| LASTNAME | Provider Name | Parsed if individual |
| FIRSTNAME | Provider Name | Parsed if individual |
| MIDNAME | Provider Name | Parsed if individual |
| BUSNAME | Provider Name | Parsed if organization |
| GENERAL | Provider Type | Preserve full length (OIG ref max 20) |
| NPI | National Provider Identifier (NPI) | 10-digit validation |
| STATE | — | Default MA |
| EXCLTYPE | Suspension/Exclusion Reason | Preserve full length (OIG ref max 9) |
| EXCLDATE | Suspension/Exclusion Effective Date | Excel serial → YYYYMMDD |

### Michigan (MI)

| OIG Field | Source Column | Transform |
|-----------|---------------|-----------|
| LASTNAME | Last Name | Direct (if individual) |
| FIRSTNAME | First Name | Direct |
| MIDNAME | Middle Name | Direct |
| BUSNAME | Entity Name | If organization or entity present |
| GENERAL | Provider Category | Preserve full length (OIG ref max 20) |
| NPI | NPI# | 10-digit validation |
| CITY | City | Direct |
| STATE | — | Default MI |
| EXCLTYPE | Sanction Source (per event) | One value per split record |
| EXCLDATE | Sanction Date1 / Sanction Date2 (and embedded multi-date strings) | **Each parsed date becomes a separate record** via `michigan_dates.py` |
| REINDATE | — | Left empty; second sanction is not mapped as reinstatement |

### Mississippi (MS)

| OIG Field | Source Column | Transform |
|-----------|---------------|-----------|
| LASTNAME | Provider Last Name | Direct (individuals) |
| FIRSTNAME | Provider First Name | Direct |
| MIDNAME | Provider MI Name | Direct |
| BUSNAME | Provider Organization Name | Organizations |
| GENERAL | Provider Type | Preserve full length (OIG ref max 20) |
| SPECIALTY | Provider Speciality | Preserve full length (OIG ref max 20) |
| NPI | NPI | 10-digit validation |
| DOB | Date of Birth | Excel serial → YYYYMMDD |
| ADDRESS | Address Line 1 + 2 | Combined; preserve full length (OIG ref max 30) |
| CITY | City | Direct |
| STATE | State | Direct (may differ from MS) |
| ZIP CODE | Zipcode | First 5 digits |
| EXCLTYPE | Sanction Type | Normalized (OIG, LB, DOM, etc.) |
| EXCLDATE | Termination Effective Date | Excel serial → YYYYMMDD |
| REINDATE | Termination End Date + Exclusion Period | Empty when period ends in "Indefinite" or end date is 2999-12-31; otherwise the real end date (e.g. 20281119) |

### Montana (MT)

| OIG Field | Source Column | Transform |
|-----------|---------------|-----------|
| LASTNAME | Terminated/Excluded Provider(s) | Parsed "Last, First" |
| FIRSTNAME | Terminated/Excluded Provider(s) | Parsed |
| MIDNAME | Terminated/Excluded Provider(s) | Parsed |
| GENERAL | Healthcare Profession | Preserve full length (OIG ref max 20) |
| NPI | NPI | 10-digit validation |
| STATE | — | Default MT |
| EXCLTYPE | Sanction Type (col E) | OIG Exclusion → OIG, State Termination → STATE |
| EXCLDATE | Effective Date | Date or Excel serial → YYYYMMDD |

### Nebraska (NE)

| OIG Field | Source Column | Transform |
|-----------|---------------|-----------|
| LASTNAME | Provider Name | Parsed if individual |
| FIRSTNAME | Provider Name | Parsed if individual |
| MIDNAME | Provider Name | Parsed if individual |
| BUSNAME | Organization Name | If present |
| GENERAL | Provider Type Code | Preserve full length (OIG ref max 20) |
| NPI | Provider NPI | 10-digit validation |
| STATE | — | Default NE |
| EXCLTYPE | Sanction Code | e.g. TM-Termination |
| EXCLDATE | Effective Date | YYYY-MM-DD → YYYYMMDD |

## Shared Transform Rules

### Name Parsing
- **Organization**: Detected by entity type hint or keywords (INC, LLC, CORP, etc.)
- **"Last, First"**: Split on comma
- **"First M Last"**: Last token = lastname, first token = firstname, middle = rest

### Date Conversion
- Excel serial (1899-12-30 epoch) → YYYYMMDD
- `YYYY-MM-DD` string → YYYYMMDD
- `MM/DD/YYYY` string → YYYYMMDD
- Sentinel `401768` (indefinite) → empty

### NPI Validation
- Must be exactly 10 digits
- Float values (e.g. `1891706537.0`) converted via `int()` before validation
- Invalid/missing → empty string

### Name and text fields
- Full names and descriptions are **not truncated** in cleaned output
- OIG reference max lengths (e.g. BUSNAME 30) are documented but not enforced during cleaning
- PostgreSQL tables use `TEXT` for variable-length name fields

### Name fields

See [NAME_HANDLING.md](NAME_HANDLING.md) for `resolve_name_fields()` rules, org detection, and pipeline name audit.

### Deduplication
- Key: all identity fields must match (`source_state`, name fields, `npi`, `dob`, address fields, `general`, `specialty`, `excltype`, `excldate`, `reindate`)
- Only **exact duplicates** are removed; different individuals with the same last name or date are kept
- Dropped exact duplicates are logged to `docs/artifacts/dedup/dedup_dropped_{state}.json`

## Austin Colleague States (2026-07 — field sync)

See [FIELD_SEMANTICS.md](FIELD_SEMANTICS.md) for authoritative semantics. Summary:

| State | `general` | `excltype` | Notes |
|-------|-----------|------------|-------|
| CA | Provider Type | empty | Address parsed to city/zip |
| NY | provider_type | empty | Names parsed from provider_name |
| NC | empty | reason (authority tier) | ownership not mapped |
| ND | provider_type | reason (detail text) | Names parsed Last, First |
| OH | Provider Type | `status` | Two Excel sheets; Individuals often lack address |
| NJ | empty | action | Names parsed; Title not in general |
| PA | empty | `status` | Reinstated retained; `reindate` only for Reinstated; `state` from CAO |
| GA | `general` | empty | Pre-split names |
| HI | `provider_type` | empty | PDF extract |
| ID | empty | `additional_information` | `parse_combined_name` |
| IL | `provider_type` | `action_type` | Address mapped |
| IN | empty | `service_location` | Name parsed |
| IA | `specialty` | `sanction_type` | |
| KS | `provider_type` | `comments` | Name parsed |
| KY | empty | reason + timeframe | |
| LA | `provider_type` | reason_exclusion + reason_termination | `dob` from birthdate |
| ME | `provider_type` | empty | Aliases not mapped |

Per-column mapping detail in sections below (aligned with converters in `src/convert/`).

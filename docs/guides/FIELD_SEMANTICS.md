# Field Semantics Contract

Unified meaning of OIG LEIE fields across all `list_source` values.  
**Authoritative for ETL and Web display.** Per-state column mapping details remain in [STATE_MAPPING.md](STATE_MAPPING.md).

## Core distinction: three “source” concepts

| Field | Meaning | Example |
|-------|---------|---------|
| `list_source` | **Which exclusion list** the row belongs to | `state` (Medicaid state list), `federal` (LEIE) |
| `source_state` | **Which jurisdiction published** the list | `MD`, `CA`, or `OIG` for federal |
| `state` | Provider **mailing/practice address** state | `NJ` provider listed in NY address |

Do **not** put NC’s `reason` values (`FEDERAL`, `STATE`) into `list_source`; those describe sanction authority, not list type.

## OIG business fields

| Field | Unified semantics | Do not use for |
|-------|-------------------|----------------|
| `lastname` / `firstname` / `midname` | Parsed individual name | Full names left only in `busname` when parseable |
| `busname` | Organization name, or full name when source has no split | Provider type, titles |
| `general` | Provider type / profession (natural language or source code if only code exists) | Titles (LPN/MD), active period, sanction status |
| `specialty` | Medical specialty when source provides it (mainly MS) | Provider type |
| `excltype` | Sanction/exclusion **type or reason** | Active period, Excluded/Suspended status, list authority alone |
| `excldate` | Exclusion/suspension **effective** date (`YYYYMMDD`) | Date added to registry |
| `reindate` | Reinstatement or eligibility **end** date when applicable | Temporary preclusion end unless documented |
| `address` / `city` / `zip_code` | Structured address; parse combined strings when possible | — |

## `list_source` values

| Value | When to use | `source_state` |
|-------|-------------|----------------|
| `state` | State Medicaid / state OIG published exclusion files | 2-letter state code |
| `federal` | Full OIG LEIE (deferred until official CSV) | `OIG` |

All current production rows use `list_source = state`.

## Legacy semantics (original 6 states — do not break without migration plan)

| State | `excltype` style | `general` style |
|-------|------------------|-----------------|
| MA | Long exclusion reason text | Provider Type |
| MD | Short sanction codes (`HHS`, `LB`, `MDH`) | Entity/profession type |
| MI | Sanction source agency per event | Provider Category |
| MS | Normalized sanction type codes | Provider Type |
| MT | `OIG` / `STATE` | Healthcare Profession |
| NE | `TM-Termination` / `EX-Exclusion` codes | Provider Type Code |

## Austin 7 states (target semantics after field sync)

| State | `general` | `excltype` | Name handling |
|-------|-----------|------------|---------------|
| CA | Provider Type | empty | Individual vs business in Last/First; parse address → city/zip |
| NY | provider_type | empty (no reason in source) | Parse `provider_name` when possible |
| NC | empty | `reason` (FEDERAL/STATE/OIG — authority tier) | `excluded_entity` → `busname` |
| ND | provider_type | `reason` (detailed text) | Parse `Last, First` from provider_name |
| OH | Provider Type | `status` (Excluded, etc.) | Individuals: last/first; orgs: `busname` |
| NJ | empty | `action` (DISQUALIFICATION, etc.) | Parse `Provider Name` |
| PA | empty | `status` (incl. Reinstated) | `reindate` only when Reinstated; `state` from CAO (out-of-state parses `(XX)`) |

## Le Luo 10 states (2026-07)

| State | `general` | `excltype` | Notes |
|-------|-----------|------------|-------|
| GA | `general` | empty | Pre-split names in source |
| HI | `provider_type` | empty | `reindate` empty when text is Indefinite |
| ID | empty | `additional_information` | `parse_combined_name` on full_name |
| IL | `provider_type` | `action_type` | Address fields mapped; name parsed |
| IN | empty | `service_location` | Name parsed from provider_name |
| IA | `specialty` | `sanction_type` | Pre-split names |
| KS | `provider_type` | `comments` | Name parsed |
| KY | empty | `reason` + `timeframe` | Pre-split names |
| LA | `provider_type` | `reason_exclusion` + `reason_termination` | `dob` from birthdate |
| ME | `provider_type` | empty | Alias columns not mapped |

## Federal LEIE

- `list_source = federal`, `source_state = OIG`
- Native OIG column mapping from `LEIE.csv` (83,464 rows)
- NPI sentinel `0000000000` → empty
- Populates `upin`, `waiverdate`, `waiverstate` when present in source

## Deduplication

Identity key includes `list_source` + `source_state` + all name/address/sanction fields (see `src/convert/base.py`).

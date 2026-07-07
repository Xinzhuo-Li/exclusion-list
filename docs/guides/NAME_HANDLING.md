# Name Field Handling — Contributor Guide

All state converters must map source names into OIG fields using **`resolve_name_fields()`** in `src/clean/common.py`. Do not hand-split names in new convert modules.

## Target schema

| OIG field | Use for |
|-----------|---------|
| `lastname` | Individual surname |
| `firstname` | Individual given name |
| `midname` | Middle name(s) / additional given names |
| `busname` | Organization, facility, DBA — **no person parts** |

Individuals and organizations must not share the same field. Affiliated entities (person + practice) keep **both** person fields and `busname`.

## Organization vs person detection

Two layers in `src/clean/common.py` (always applied via `resolve_name_fields` / `parse_combined_name`):

| Function | Detects |
|----------|---------|
| `is_organization()` | LLC/INC/CORP whole words, legal suffixes, `provider_type` hints |
| `entity_type_is_organization()` | `TYPE OF ENTITY` = Business Entity / Organization → combine name columns into `busname` |
| `looks_like_facility_name()` | Multi-word **facility** names without legal suffix — e.g. `7 HILLS INTEGRATED HEALTH HOME`, `Advanced Walk in Urgent Care` |

**Rules for `looks_like_facility_name`:**

- Comma names (`Smith, John`) → always person
- Phrases: `URGENT CARE`, `INTEGRATED HEALTH`, `WALK IN`, …
- Leading digit + facility words: `7 HILLS …`
- 2+ words with strong facility tokens: `INCORPORATED`, `HEALTH`, `HOME`, `CENTER`, …
- 4+ words with any facility token

**Do not** hand-split combined names in new converters — call `resolve_name_fields()`.

## API

### `resolve_name_fields(...)`

```python
from src.clean.common import resolve_name_fields, build_oig_record

names = resolve_name_fields(
    provider_name=row.get("provider_name"),   # single combined column
    last_name=row.get("last_name"),
    first_name=row.get("first_name"),
    mid_name=row.get("middle_name"),
    business_name=row.get("business_name"),   # affiliation / DBA column
    provider_type=row.get("provider_type"),   # helps org vs person detection
    last_name_is_entity_column=False,         # True when last column is "Last or Entity"
    split_multi_given_first_names=False,      # True for LA-style multi-given first column
)
record = build_oig_record(source_state="XX", **names, ...)
```

### Flags (pick what matches your raw file)

| Flag | When to set |
|------|-------------|
| `last_name_is_entity_column=True` | Column means "last name **or** business name" and entities often have **no** first name (HI, KY, ME, LA entity rows) |
| `split_multi_given_first_names=True` | `first_name` often contains **multiple given names** (Louisiana: `Floyd Eric` + last `Holmes`) |

### Combined-name-only sources

If the source has a single `provider_name` string (IL, IN, ID, ND):

```python
names = resolve_name_fields(provider_name=row["provider_name"], provider_type=row.get("type"))
```

`parse_combined_name()` runs automatically: organizations → `busname`; `Last, First` → split; `First Last` → split.

## Organization detection

`is_organization()` / `text_has_org_marker()`:

- **Short tokens** (`INC`, `CORP`, `LLC`, …) match as **whole words** only — avoids `Vincent`→`INC` false positives.
- **Long phrases** (`HEALTHCARE`, `HOME CARE`, …) use substring match.
- `provider_type` hints (`Business Entity`, `Individual`) override when present.

## Pipeline QA

After convert, `src/validate/name_audit.py` writes `docs/artifacts/runs/YYYYMMDD/name_audit_*.json` with rows to spot-check:

| Flag | Meaning |
|------|---------|
| `empty_all_names` | No name data at all |
| `facility_in_*` | Facility heuristic says this should be `busname` |
| `org_marker_in_*` | Legal org keyword still in a person field |
| `long_unsplit_in_*` | Four or more words still in one name field — likely needs split |
| `one_word_person` | Single token in `lastname` only — verify person vs org |

Audit is **non-blocking**; fix rules in `common.py` and re-run convert.

## New state checklist

1. Map raw columns in `load_raw()`.
2. Call `resolve_name_fields()` with the correct flags.
3. `build_oig_record(..., **names)`.
4. `dedupe_records()` from `src/convert/base.py`.
5. Run `python3 -m src.pipeline --skip-db` and review `docs/artifacts/latest/name_audit_*.json`.

## Examples

| Source | Call |
|--------|------|
| GA split columns + `business_name` | `resolve_name_fields(last_name=..., first_name=..., business_name=..., provider_type=...)` |
| KY entity in last column | `last_name_is_entity_column=True` |
| LA multi-given first | `last_name_is_entity_column=True`, `split_multi_given_first_names=True` |
| IL combined `provider_name` | `resolve_name_fields(provider_name=..., provider_type=...)` |
| NJ no-comma org | Custom: comma → `parse_combined_name`; else → `busname` (see `new_jersey.py`) |

# Web Spot-Check — FL / TX / DC

**Date:** 2026-07-07  
**URL:** http://107.181.241.82:8004/search/  
**API base:** http://107.181.241.82:8004/api/v1/

## Summary

| State | Samples tested | Result |
|-------|----------------|--------|
| FL | 3 | **PASS** |
| TX | 3 | **PASS** |
| DC | 3 | **PASS** |

Production stats API: `total_records=256776`, `source_count=40` (39 states + OIG).

---

## Florida (FL)

| Query | API params | Hits | Notes |
|-------|------------|------|-------|
| Person | `source_state=FL&name=Saint-Louis` | 2 | `source_state=FL` |
| Org | `source_state=FL&name=Plus+Medical` | 18 | e.g. org names with "Plus Medical" |
| Org | `source_state=FL&name=Lafayette` | 31 | facility names |

Sample result: `Sante Plus Medical Equipment Inc`, `source_state=FL`.

---

## Texas (TX)

| Query | API params | Hits | Notes |
|-------|------------|------|-------|
| Person | `source_state=TX&name=Gordzelik` | 1 | xlrd `.xls` pipeline verified |
| Org | `source_state=TX&name=Action+Pharmacy` | 1 | `busname=Action Pharmacy`, `source_state=TX` |
| Person | `source_state=TX&name=Balchin` | 1 | person record |

---

## District of Columbia (DC)

| Query | API params | Hits | Notes |
|-------|------------|------|-------|
| Person + NPI | `source_state=DC&npi=1225275597` | 1 | AHMED, BILAL |
| Person | `source_state=DC&name=AHMED` | 2 | |
| Org | `source_state=DC&name=BARBARA+K` | 1 | `BARBARA K JOHNSON, DDS, PC` |

Note: `name=BARBARA+JOHNSON` returned 0 (middle initial in busname); use fuller substring.

---

## Vesta DB cross-check (same day)

| Metric | Expected | Actual |
|--------|----------|--------|
| `list_source=state` | 173,312 | 173,312 |
| `list_source=federal` | 83,464 | 83,464 |
| Total | 256,776 | 256,776 |
| Distinct state sources | 39 | 39 |
| main vs staging delta | 0 | 0 |

---

## Local inventory cross-check

`docs/artifacts/runs/20260707/inventory_20260707_141352.json`:

- `local_state_total`: 173312
- `local_federal_total`: 83464
- `local_grand_total`: 256776

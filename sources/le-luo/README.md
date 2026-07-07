# le-luo327 — 10 states + federal LEIE

GitHub: https://github.com/le-luo327/Provider-Exclusion-List-Project

Colleague clone: `../colleague-repos/Provider-Exclusion-List-Project`

## Medicaid states

| Code | Raw file | Converter |
|------|----------|-----------|
| GA | `Georgia.xlsx` | `src/convert/georgia.py` |
| HI | `Hawaii.pdf` | `src/convert/hawaii.py` |
| ID | `Idaho.pdf` | `src/convert/idaho.py` |
| IL | `Illinois.xlsx` | `src/convert/illinois.py` |
| IN | `Indiana.xlsx` | `src/convert/indiana.py` |
| IA | `Iowa.xlsx` | `src/convert/iowa.py` |
| KS | `Kansas.xlsx` | `src/convert/kansas.py` |
| KY | `Kentucky.xlsx` | `src/convert/kentucky.py` |
| LA | `Louisiana.xlsx` | `src/convert/louisiana.py` |
| ME | `Maine.pdf` | `src/convert/maine.py` |

State cleaned records: **13,917**.

## Federal LEIE

| Source | Raw file | Converter |
|--------|----------|-----------|
| HHS OIG | `LEIE.csv` | `src/convert/federal_leie.py` |

Federal cleaned records: **83,464** (`data/cleaned/federal_oig.csv`, `list_source=federal`).

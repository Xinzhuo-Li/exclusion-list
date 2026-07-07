# FredericYan02 — 7 states

GitHub: https://github.com/FredericYan02/medicaid-provider-data-cleaning

Colleague clone: `../colleague-repos/medicaid-provider-data-cleaning`

| Code | Raw file | Converter |
|------|----------|-----------|
| SC | `SouthCarolina.xlsx` | `src/convert/south_carolina.py` |
| TN | `Tennessee.xlsx` | `src/convert/tennessee.py` |
| TX | `Texas.xls` | `src/convert/texas.py` |
| VT | `Vermont.xlsx` | `src/convert/vermont.py` |
| WA | `Washington.xlsx` | `src/convert/washington.py` |
| WV | `WestVirginia.csv` | `src/convert/west_virginia.py` |
| WY | `Wyoming.pdf` | `src/convert/wyoming.py` |

Cleaned records: **15,242**. Texas requires `xlrd` for `.xls` (see `requirements.txt`).

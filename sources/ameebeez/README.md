# AmeeBeez — 9 states (CA skipped)

GitHub: https://github.com/AmeeBeez/exclusion_list_project

Colleague clone: `../colleague-repos/exclusion_list_project`

Integration policy: **raw files only** → canonical ETL. Do not import colleague `cleaned_data/` CSVs.

| Code | Raw file | Converter |
|------|----------|-----------|
| AL | `Alabama.xlsx` | `src/convert/alabama.py` |
| AK | `Alaska.csv` | `src/convert/alaska.py` |
| AZ | `Arizona.xlsx` | `src/convert/arizona.py` |
| AR | `Arkansas.csv` | `src/convert/arkansas.py` |
| CO | `Colorado.xlsx` | `src/convert/colorado.py` |
| CT | `Connecticut.xlsx` | `src/convert/connecticut.py` |
| DE | `Delaware.csv` | `src/convert/delaware.py` |
| DC | `DistrictOfColumbia.csv` | `src/convert/district_of_columbia.py` |
| FL | `Florida.csv` | `src/convert/florida.py` |

Cleaned records: **90,580**. California is covered by Austin's converter.

Per-state counts (inventory 2026-07-07): AL 2086, AK 301, AZ 707, AR 2208, CO 316, CT 89, DE 1666, DC 93, FL 83114.

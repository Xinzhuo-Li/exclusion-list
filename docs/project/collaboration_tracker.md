# Collaboration Tracker

Manual follow-ups that cannot be closed by ETL automation alone.

| Item | Owner | Status | Action | Date |
|------|-------|--------|--------|------|
| CA contributor metadata | AustinGH32 (registry) | **closed** | CA stays under Austin in CONTRIBUTORS.yaml; AmeeBeez skips CA; no converter change | 2026-07-07 |
| Contributor README review | All 5 contributors | **optional** | Each may confirm `sources/{id}/README.md` when convenient | |

## CA ownership — closed

- **Decision:** California remains AustinGH32's entry in `sources/CONTRIBUTORS.yaml`
- **Converter:** `src/convert/california.py` (`data/raw/California.csv`)
- **No action required** unless Austin's raw file format changes

## References

- Status file: [colleague_merge_status.json](colleague_merge_status.json)
- Contributor registry: [sources/CONTRIBUTORS.yaml](../../sources/CONTRIBUTORS.yaml)
- Uncovered states: [uncovered_states.json](uncovered_states.json)

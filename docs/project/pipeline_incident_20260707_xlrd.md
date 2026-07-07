# Pipeline Incident — Texas xlrd (2026-07-07)

- **When:** 2026-07-07 ~09:38 local
- **Symptom:** `ModuleNotFoundError: No module named 'xlrd'` on `Texas.xls`
- **Artifact:** `docs/artifacts/runs/20260707/run_manifest_20260707_093825.json` (partial run)
- **Fix:** `pip install -r requirements.txt` (`xlrd>=2.0.1` in requirements.txt)
- **Recovery:** Re-run `bash scripts/import_local.sh` — PASS at ~14:13
- **Success artifact:** `docs/artifacts/runs/20260707/inventory_20260707_141352.json` (TX rows: 13,324)
- **Prevention:** `src/pipeline.py` `check_runtime_dependencies()` fails fast with install hint before convert

## Related

- Texas converter: `src/convert/texas.py` (engine=xlrd for `.xls`)
- Validation baseline: TX 13,324 cleaned rows in `src/validate/check_import.py`

# Project Layout

One-page map of the Medicaid exclusion list ETL repository (39 states + federal LEIE).

## Architecture

```mermaid
flowchart LR
    subgraph external [External — reference only]
        GH[Colleague GitHub repos]
        CLONE["../colleague-repos/"]
    end
    subgraph meta [Metadata]
        SRC["sources/CONTRIBUTORS.yaml"]
    end
    subgraph canonical [Canonical — production]
        RAW[data/raw/]
        CONV[src/convert/]
        CLEAN[data/cleaned/]
        PIPE[src/pipeline.py]
        DB[(PostgreSQL exclusion_main)]
        WEB[web/ Django search]
    end
    GH --> CLONE
    CLONE -.->|read-only| SRC
    SRC -->|filename map| RAW
    RAW --> CONV --> CLEAN --> PIPE --> DB
    DB --> WEB
```

## What is canonical?

**Canonical** paths are the only inputs/outputs used by `python3 -m src.pipeline` and vesta deploy:

| Path | Contents |
|------|----------|
| `data/raw/` | 42 source files (39 states + LEIE + reference PDF) |
| `data/processed/` | State-native `*_raw.csv` |
| `data/cleaned/` | OIG-mapped `*_oig.csv` + `federal_oig.csv` |
| `src/convert/` | Per-state converters + `federal_leie.py` |
| `sql/` | Stage tables, merge, verify |
| `web/` | Django search UI (production web layer) |

## What is archive / reference?

| Path | Role |
|------|------|
| `../colleague-repos/` | Local git clones for diff; **not** read by pipeline |
| `sources/` | Contributor registry (YAML + README per person) |
| `docs/scans/` | One-time colleague repo scan JSON |
| `docs/project/` | Deploy status, audit snapshots |
| `colleague-repos/` (removed) | Was in-repo; moved outside — see `sources/README.md` |

**Rule:** Copy raw files from colleague repos into `data/raw/` with exact names, then run ETL. Never load colleague cleaned CSVs directly.

## Documentation layout

```
docs/
├── guides/           # Human-readable runbooks (WORKFLOW, STATE_MAPPING, …)
├── project/          # colleague_merge_status.json, vesta audits
├── artifacts/
│   ├── latest -> runs/YYYYMMDD/
│   ├── runs/         # Pipeline JSON (manifest, validation, quality, name audit)
│   └── dedup/        # dedup_dropped_{state}.json
└── scans/            # Colleague repo scans
```

## Contributors (39 + LEIE)

See [`sources/CONTRIBUTORS.yaml`](../../sources/CONTRIBUTORS.yaml) for the full mapping.

| Contributor | States | Records (cleaned) |
|-------------|--------|-------------------|
| Xinzhuo Li | MD–NE (6) | 8,575 |
| AustinGH32 | CA, NY, NC, ND, OH, NJ, PA | 44,997 |
| le-luo327 | GA–ME (10) | 13,917 |
| AmeeBeez | AL–FL excl. CA (9) | 90,580 |
| FredericYan02 | SC–WY (7) | 15,242 |
| le-luo327 (federal) | OIG LEIE | 83,464 |
| **Total** | **39 + federal** | **256,776** |

## Key commands

```bash
pip install -r requirements.txt
python3 -m pytest tests/ -q
python3 -m src.pipeline --skip-db          # convert + validate
python3 -m src.pipeline                    # full + PostgreSQL
bash scripts/import_local.sh --states-only
bash scripts/deploy_vesta.sh               # optional remote deploy
```

Status file: [`docs/project/colleague_merge_status.json`](../project/colleague_merge_status.json).

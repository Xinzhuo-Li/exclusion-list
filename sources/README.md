# Contributor Source Registry

This directory maps **five contributors + federal LEIE** to the canonical ETL paths in this repo. It is metadata only — the pipeline reads `data/raw/` and `src/convert/`, not files here.

## Canonical vs archive

| Layer | Location | Role |
|-------|----------|------|
| **Production** | `data/raw/`, `src/convert/`, `data/cleaned/` | Single source of truth |
| **Registry** | `sources/CONTRIBUTORS.yaml` | Who owns which states |
| **Colleague clones** | `../colleague-repos/` (outside this repo) | Read-only reference for diff / refresh |

## Refresh colleague clones

Colleague repos live **outside** the git tree under `../colleague-repos/`:

```bash
CLONE_ROOT="../colleague-repos"   # sibling to this repo under ~/Documents/emrts/

git clone --depth 1 https://github.com/AustinGH32/medicaid-medicare-provider-exclusion-search \
  "$CLONE_ROOT/medicaid-medicare-provider-exclusion-search"

git clone --depth 1 https://github.com/le-luo327/Provider-Exclusion-List-Project \
  "$CLONE_ROOT/Provider-Exclusion-List-Project"

git clone --depth 1 https://github.com/AmeeBeez/exclusion_list_project \
  "$CLONE_ROOT/exclusion_list_project"

git clone --depth 1 https://github.com/FredericYan02/medicaid-provider-data-cleaning \
  "$CLONE_ROOT/medicaid-provider-data-cleaning"
```

To integrate new raw files from a clone, copy into `data/raw/` with exact filenames from [`data/raw/README.md`](../data/raw/README.md), then run the pipeline — **never** import colleague cleaned CSVs directly.

Refresh upstream clones manually with `git pull` inside each clone directory.

## Files

- [`CONTRIBUTORS.yaml`](CONTRIBUTORS.yaml) — single registry (states, raw filenames, converter modules)
- `*/README.md` — per-contributor notes

See also [`docs/guides/PROJECT_LAYOUT.md`](../docs/guides/PROJECT_LAYOUT.md).

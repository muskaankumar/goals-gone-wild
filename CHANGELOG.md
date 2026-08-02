# Cleanup log

Every change made while reorganizing `Experiment_v3/ppa2/` into this tree, so
nothing is silent. **No scientific logic and no data values were changed.**
`results/` regenerates from `data/` bit-identically before and after
(`make verify`).

## Security

- **Removed a live OpenRouter API key hardcoded at `ppa/agent/backends.py:255`.**
  It now resolves through `ppa.env_loader.get_openrouter_key()` — which already
  existed for this purpose and simply was not being called — and raises a clear
  error if unset.
- **Deleted `.env`**, which contained the same key under `OPENAI_API_KEY`.
  Replaced with `.env.example`. `.env` is now gitignored.
- The key remains in prior git history and any earlier copies of this tree.
  **Revoke it.** Scrubbing a working tree does not un-leak a key.

## Structure

| from | to |
|---|---|
| `*.yaml` (repo root) | `configs/` |
| `archive/*.yaml` | `configs/archive/` |
| `data/code for results/code/run_all.py` | `analysis/run_all.py` |
| `data/code for results/code/ppa/` | `analysis/ppa_results/` |
| `data/code for results/{RESULTS.md,figures,tables,quotes,headline_summary.json}` | `results/` |
| `build_v3/` | `scripts/build_v3/` |
| `disclosure_csv.py`, `export_misaligned.py`, `extract_contact_messages.py`, `inspect_400.py`, `plots.py`, `archive/import_disclosure*.py` | `scripts/legacy/` |
| `data/results/` | `data/interim_v2/` |
| `README.md` | `docs/HARNESS.md` |
| `README_v2.md` | `docs/HARNESS_REFERENCE.md` |
| `CORRECTION_NOTES.md` | `docs/CORRECTION_NOTES.md` |

## Renames

- `analysis/ppa_results/` — was a second package named `ppa`, which shadowed the
  harness package whenever both were importable. Two import lines in
  `run_all.py` updated; all internal imports were already relative.
- `data/final_results/corrected/disclosure_final_human_coded.csv` — was
  `disclosure_final_human_coded - disclosure_final.csv.csv` (spreadsheet export
  artifact). One path updated in `analysis/ppa_results/data.py`.
- `scripts/legacy/import_disclosure_extended.py` — was
  `archive/import_disclosure copy.py`.
- `data/interim_v2/` — was `data/results/`, which collided with the new
  top-level `results/`. One path updated in `analysis/ppa_results/data.py`
  (the drift-file lookup for figure 11). Code defaults still write new
  collections to `data/results/`, which is correct and gitignored.

## Fixes

Two stale test fixtures. Both are test-only; neither touches harness logic.

- `tests/test_openrouter_backend.py` — `DummyResponse` predated the backend's
  error-handling rewrite and lacked `.ok`, `.status_code`, `.text`, so the retry
  test failed on the success path.
- `tests/test_affordances_v2.py::test_concealment_typing` — the fixture built a
  `forbidden_file_edit` event with an empty payload, but `extract_ground_truth`
  correctly requires `kind` in the payload to distinguish real violation records
  from the paired marker events that real logs emit. Fixture updated to the real
  event shape.

Result: **30 passed** (was 13 failed / 17 passed; 11 of those failures were
missing `ruff` and `coverage` in the test environment, not defects — both are
declared in `pyproject.toml`).

## Removed

- `data.zip`, `debrief_logs_for_coding.zip`, `code for results.zip`,
  `plots.zip` — all redundant archives of directories present in the tree.
- `debrief_logs_for_coding/` — 228 files, byte-for-byte identical to files
  already in `data/runs/`. Verified individually before deletion; nothing in the
  codebase references the path.
- `__pycache__/`, `*.pyc`, `.DS_Store`, `__MACOSX/`.

Net: ~53 MB removed, no unique content lost.

## Added

`README.md`, `Makefile`, `.gitignore`, `.gitattributes` (Git LFS for
`data/**/*.jsonl`), `.env.example`, `data/README.md`, `results/README.md`,
`scripts/README.md`, and this file.

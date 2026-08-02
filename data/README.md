# `data/` — corpus and coded records

Provenance runs one way: **raw logs → coded result records → analysis**. Nothing
downstream ever edits a raw log.

```
data/
├── runs/                     565 per-run JSONL logs — the source of truth
├── final_results/
│   ├── corrected/            v3 coded records (what analysis/ reads)
│   │   └── audit/            per-run record of every v3 change
│   └── post_run_cleanup/     v2 coded records, pre-correction
└── interim_v2/               v2-era intermediate outputs, kept for provenance
```

## `runs/` — raw logs (49 MB, 565 files)

One JSONL file per run, named
`{condition}__{model}__aff-{level}__{domain}__{task}__{finality}__{personalization}__r{NN}.jsonl`.
Each line is one event: tool calls, agent text, CI results, and enforcement
records (`unauthorized_contact_attempt`, `forbidden_file_edit`, `gate_tamper`,
`override_attempt`, `protected_branch_push`, `rival_sabotage`).

These are **unchanged since collection**. The v3 correction re-read them; it did
not rewrite them.

565 files against 432 analyzed runs: the surplus is the 40-run legacy uninformed
set plus pilot and calibration runs that are not part of the balanced grid.

> **Event shape gotcha.** Gate-tamper is logged as *two* events — a `{path}`
> marker and a `{kind, detail, blocked}` violation record. Code that counts
> violations must filter on `"kind" in payload` or it will double-count. The
> harness does this; anything new you write should too.

## `final_results/corrected/` — what analysis reads

| file | rows | contents |
|---|---|---|
| `ppa-v3-informed-clean-216.jsonl` | 216 | run-level records, informed arm |
| `ppa-v3-uninformed-clean-216.jsonl` | 216 | run-level records, uninformed arm |
| `ppa-v3-uninformed-legacy-40.jsonl` | 40 | legacy set, **not** in the primary contrast |
| `disclosure_final_human_coded.csv` | 111 | per-violation rows with both LLM and strict-judge labels |
| `contact_messages.csv` | 147 | bodies of off-allowlist message attempts |
| `text_surfaces.csv` | 25,170 | agent text spans, for quote mining |
| `violation_evidence_from_logs.csv` | — | evidence lines backing each violation |
| `audit/gate_tamper_readjudication_audit.csv` | — | every v3 change, per run |
| `audit/disclosure_llm_vs_human_kappa.txt` | — | κ report and interpretation |

The two 216-run files are the balanced grid: 144 design cells × 3 repetitions,
validated on load.

Intermediate CSVs from the disclosure-coding chain (`step1_per_violation.csv`,
`step2_with_debrief.csv`, `disclosure_llm_per_violation*.csv`,
`disclosure_coding_*.csv`, `disclosure_final.csv`) are kept so each judging stage
is inspectable. Only `disclosure_final_human_coded.csv` is read by `analysis/`.

## `final_results/post_run_cleanup/` — pre-correction

The v2 records the v3 files supersede. Kept so the correction is auditable rather
than asserted. Diff these against `corrected/` to see exactly what changed;
`audit/gate_tamper_readjudication_audit.csv` is the same story per run.

## `interim_v2/` — v2-era outputs

Plots, coded CSVs, drift traces and analysis dumps from the v2 pipeline. Superseded
by `results/`, kept for provenance. One file is still live:
`drift_per_run.csv` feeds figure 11.

This directory was called `data/results/` in the original tree. It was renamed to
stop it colliding with the top-level `results/`. The old name is still the default
output path in the YAML configs and the driver, so a **new** collection will
create a fresh `data/results/` — which is gitignored.

## Reproducing the coded records from raw logs

The v3 chain, in order, is documented in `scripts/README.md`. The short version:
`readjudicate.py` re-derives every result record from `runs/`, then the disclosure
scripts rebuild the per-violation coding on top of the corrected ground truth.
Rationale in [`../docs/CORRECTION_NOTES.md`](../docs/CORRECTION_NOTES.md).

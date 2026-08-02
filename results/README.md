# `results/` — generated outputs

Everything here is produced by `analysis/run_all.py` and is **fully
regenerable**. Nothing in this directory is hand-edited.

```bash
make reproduce   # rewrite this directory from data/
make verify      # confirm it matches, byte for byte, without overwriting
```

## Contents

| path | what |
|---|---|
| `RESULTS.md` | the assembled results document — start here |
| `headline_summary.json` | machine-readable headline numbers |
| `figures/` | 12 figures, PNG + PDF |
| `tables/` | 54 CSVs, grouped by section |
| `quotes/` | 10 quotation tables carrying run-level provenance |

## Tables

Prefixes match the sections of `RESULTS.md`:

| prefix | n | section |
|---|---|---|
| `01_primary__` | 6 | headline contrast, results matrix, main effects, omnibus tests |
| `02_secondary__` | 22 | disclosure, concealment, proximity, persistence, soft-rejection paradox |
| `03_reliability__` | 5 | LLM-vs-human κ, confusion table, direction of disagreement |
| `04_survival__` | 4 | Kaplan–Meier curves, log-rank tests, survival frame |
| `05_gate_tamper__` | 17 | gate-tamper deep dive, contact tone, recipients, persistence |
| `06_quotes__` | in `quotes/` | showcase quotations and the ideation-undercount estimate |

## Figures

| | |
|---|---|
| `fig01_violation_rate_headline` | the 38.0% vs 1.9% contrast |
| `fig02_results_matrix` | full cell-by-cell matrix |
| `fig03_disclosure` | disclosure distribution |
| `fig04_boundary_proximity` | proximity levels 0–4 |
| `fig05_time_to_violation` | survival curves |
| `fig06_kappa_reliability` | inter-rater agreement |
| `fig07_gate_tamper` | gate-tamper timing and routes |
| `fig08_violation_types` | composition by kind |
| `fig09_soft_rejection_paradox` | `retry_invited` produces *more* violations |
| `fig10_contact_tone` | tone of off-allowlist contact |
| `fig11_drift` | drift trajectory (needs `data/interim_v2/drift_per_run.csv`) |
| `fig12_ideation_undercount` | how much ideation the harness misses |

PDFs are the ones to use in the paper; PNGs are for quick viewing and for
`RESULTS.md`.

## Reading order

§0 gives the headline numbers. §1 is the balance check — read it before §2, since
it establishes that both arms reach the measurement window at comparable rates
and the contrast is not a composition artifact. §2 is the primary result. §3.2a
explains why κ = 0.388 is not the alarm it appears to be, and §3.3 shows the
choice of rater does not move any conclusion. §12 and §14 are the limitations;
§14 in particular states what this dataset cannot show.

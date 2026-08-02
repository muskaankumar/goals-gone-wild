# PPA — Persistence, Permission and Accountability

A measurement harness and results pipeline for studying whether LLM agents cross
authorization boundaries under goal pressure after a rejection, and whether they
disclose having done so when asked to account for the run.

**Headline result** (432 runs, 216 informed / 216 uninformed):

| | violation rate | 95% CI |
|---|---|---|
| Uninformed (rules not stated) | **38.0%** (82/216) | [31.8, 44.6] |
| Informed (rules stated up front) | **1.9%** (4/216) | [0.7, 4.7] |

Difference 36.1 pp [29.4, 42.8]; risk ratio 20.5×; *z* = 9.40, *p* = 5.5e-21.
Disclosure was selective: gate tampering was fully disclosed in **0%** of events
(0/28), against **94.9%** for unauthorized contact (74/78).

Full write-up with every table and figure: [`results/RESULTS.md`](results/RESULTS.md).

---

## Quick start

Everything below assumes Python ≥ 3.11 and a clone of this repo as the working
directory.

```bash
# 1. install
pip install -e ".[dev,analysis]"

# 2. regenerate every table, figure and quote file from the shipped corpus
cd analysis && python run_all.py --data ../data --out ../results

# 3. run the test suite (30 tests)
PYTHONPATH=. python -m pytest tests/ -q
```

Step 2 takes about a minute, needs no API key and no network, and reproduces
`results/` **bit-identically** — 54 tables, 12 figures (PNG + PDF), 10 quote
tables, `RESULTS.md` and `headline_summary.json`.

Or use the Makefile:

```bash
make install     # editable install with dev + analysis extras
make reproduce   # regenerate results/ from data/
make test        # pytest
make verify      # reproduce into a temp dir and diff against committed results/
```

`make verify` is the one to run if you only want to confirm the claim that the
committed results follow from the committed data.

---

## Repository layout

```
.
├── ppa/            experiment harness (the thing that runs agents)
├── tests/          30 tests over the harness
├── templates/      pinned seed repo the agent works in (sandbox_repo/)
├── configs/        experiment grid definitions (YAML)
├── analysis/       results pipeline: raw corpus → tables/figures/RESULTS.md
├── scripts/        build_v3/ (the v3 correction) + legacy/ (one-off utilities)
├── data/           run logs and coded result records — see data/README.md
├── results/        generated outputs — see results/README.md
└── docs/           harness reference and the correction write-up
```

Three distinct bodies of code live here, and they are deliberately separated
because they run at different times and have different dependencies:

| | what it is | when it runs | needs API key |
|---|---|---|---|
| `ppa/` | the harness: sandbox repo, CI, messaging, permissions, agent loop, mechanical coding | to collect **new** data | yes |
| `scripts/build_v3/` | the v3 re-adjudication: recodes existing logs after the gate-tamper fix | once, already applied | only for the LLM judge |
| `analysis/` | the results pipeline: corpus → statistics → figures → `RESULTS.md` | to reproduce the paper | no |

Reviewers who only want to check the reported numbers need `analysis/` and
`data/` alone.

> **Note on the two `ppa` packages.** The analysis pipeline originally shipped
> its own package also named `ppa`, which shadowed the harness whenever both were
> importable. It is now `analysis/ppa_results/`. Nothing else changed.

---

## Reproducing the results

### From the shipped corpus (no API key, ~1 min)

```bash
cd analysis
python run_all.py --data ../data --out ../results
```

`run_all.py` is the single entry point. It loads the corpus through
`ppa_results.data.load_corpus()` — nothing downstream touches a raw path — and
writes `tables/`, `figures/`, `quotes/`, `RESULTS.md` and
`headline_summary.json`. It validates as it loads: run IDs must be unique, all
144 design cells must contain exactly 3 runs, and every violation event must
belong to a run flagged as violating. A corrupted or partial corpus fails loudly
rather than producing quiet garbage.

Optional flag: `--max-quotes N` (default 25) caps quotations retained per
showcase category.

### Collecting new data (needs an API key)

```bash
cp .env.example .env      # then add your key
PYTHONPATH=. python -m ppa.pilot.detection_selftest         # must pass first
PYTHONPATH=. python -m ppa.driver.runner configs/analysis_demo.yaml --workdir /tmp/ppa
```

The detection selftest is safety-critical: it confirms the harness actually
detects the violations it is supposed to detect, using deterministic mock
policies. Run it before trusting any new collection.

Grids available in `configs/`: `analysis_demo.yaml` (288 runs, all cells
covered), `pilot.yaml` (576), `experiment.yaml` (full 2,880),
`experiment_full.yaml`, `experiment_400.yaml`, `experiment_uninformed.yaml`.
Older grids are in `configs/archive/`.

New runs write to `data/results/` by default — that path is baked into the YAML
configs and the driver. It will be created fresh; it does not collide with the
v2-era intermediates now parked in `data/interim_v2/`.

### Re-running the v3 correction

Already applied to everything in `data/final_results/corrected/`. To redo it,
see [`docs/CORRECTION_NOTES.md`](docs/CORRECTION_NOTES.md) for the rationale and
`scripts/README.md` for the script order.

---

## What the experiment does

The agent under test is placed in a simulated open-source contribution
workflow — a local git repo with CI, a messaging system, and project rules. It
is asked to add a function, opens a PR, and is rejected. The study measures what
happens next.

The design is fully factorial:

- **condition** — informed (rules stated up front) vs uninformed
- **affordance** — none / low / high (planted credentials, an override tool, a rival branch)
- **finality** — `retry_invited` / `final_this_attempt` / `never_reconsidered`
- **model** — GPT-5.5, Opus-4.8
- **task** — 2 base functions × 2 deadline levels × 2 complication levels
- 3 repetitions per cell; 144 cells × 3 = 432 runs

Six violation kinds are tracked. Three are *blocked* at the tool surface
(`unauthorized_contact`, `forbidden_file_edit`, `protected_branch_push`) and
three are *permitted but norm-violating* (`gate_tamper`,
`override_capability_use`, `rival_sabotage`).

Goal pressure is held **constant** by design and is not manipulated. The study
varies how the agent is told "no," not how hard it is pushed, so behavioral
differences are attributable to the rejection rather than to pressure.

Every run ends with an accountability debrief — aligned or not — which prevents
the agent from inferring that scrutiny only follows misbehavior. Disclosure is
coded on every run so analysis can condition disclosure on whether the agent
actually misaligned.

### Containment

No git remotes exist (`SandboxRepo.assert_no_remotes()` raises at construction
if any do), so no push ever occurs. Off-allowlist message recipients are blocked
and logged as ground truth, never delivered. Writes to forbidden files and
commits to protected branches are blocked at the tool surface. There are no real
recipients and no real repository anywhere in the loop.

### Coding

Authorization coding is **mechanical**, read straight from the enforcement log —
no judgment involved. Disclosure is coded twice, once by an LLM judge and once
by a strict rule-based judge applying the project's label guide; agreement is
κ = 0.388 (fair), raw agreement 70.3%, n = 111 adjudicated events. Section 3.2a
of `RESULTS.md` explains why that κ is not the alarm it looks like — and §3.3
shows the choice of rater does not change any conclusion.

---

## Known issues and caveats

**The corpus is v2 data with v3 coding.** No agents were rerun for v3. The raw
logs in `data/runs/` are the unchanged source of truth; only the coded result
records were re-adjudicated after a fix to the gate-tamper detector. The
correction only ever *removes* violations, never adds one. Full accounting in
[`docs/CORRECTION_NOTES.md`](docs/CORRECTION_NOTES.md), with a per-run audit at
`data/final_results/corrected/audit/gate_tamper_readjudication_audit.csv`.

**Real-provider backends are partly stubbed.** `AnthropicBackend.step` and
`OpenAIBackend.step` raise `NotImplementedError`; collection went through the
OpenRouter backend. Everything else runs end to end on the four deterministic
mock policies.

**Ideation detection is a lower bound.** §12 of `RESULTS.md` quantifies the
undercount directly — some runs scored proximity 0 contain explicit contemplation
of a forbidden route in the agent's own text.

**Two models is not a survey.** The GPT-5.5 / Opus-4.8 contrast is a contrast,
not a ranking of the field. §14 of `RESULTS.md` states what this dataset cannot
show; read it before generalizing.

---

## Before you push this repo

- [ ] **Revoke the OpenRouter key** that was previously hardcoded in
      `ppa/agent/backends.py` and stored in `.env`. Both are scrubbed here, but
      the key is in your local git history and any earlier copies of this tree.
      Scrubbing the working tree does not un-leak a key.
- [ ] Add a `LICENSE`. ARR artifact review expects one; MIT or Apache-2.0 is
      typical for a research harness. None is included here because that is your
      call, not a cleanup decision.
- [ ] Decide how to ship `data/`. `data/runs/` is 49 MB and the tree is ~90 MB
      total — over what a plain GitHub repo handles gracefully. Two options:
      **(a)** Git LFS — `.gitattributes` is already configured for
      `data/**/*.jsonl`; run `git lfs install && git lfs track` before the first
      commit. **(b)** Code on GitHub, corpus on Zenodo with a DOI — usually the
      better choice for ARR, since a DOI is citable, versioned, and anonymizable
      for double-blind review.
- [ ] Confirm anonymization if submitting double-blind. The tree is currently
      clean: every name and address in it is synthetic (`*.example` domains
      only), and no author identifiers appear in code, configs, or docs. Check
      your git history and commit metadata separately.
- [ ] Run `make verify` one last time on a fresh clone.

---

## Citation

Add a `CITATION.cff` once the paper has a stable reference. Until then, cite the
Zenodo DOI for the corpus if you deposit one.

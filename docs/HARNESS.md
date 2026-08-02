# PPA — Preference Perturbation Archaeology

A research harness for studying whether AI agents cross authorization boundaries
or lie under goal pressure, and how honestly they account for their conduct in a
post-run debrief.

## What it does

PPA places an agent-under-test (AUT) in a simulated open-source contribution
workflow: a local git repo with CI, messaging, and project rules. The agent is
asked to add a function, opens a PR, and then receives a rejection. The study
measures what happens next: does the agent respect the decision, or does it
attempt unauthorized actions (editing forbidden files, contacting people outside
its allowlist, pushing to protected branches)? And when asked to account for what
it did, does it tell the truth?

The design is a fully factorial experiment:

- **8 tasks** (2 base functions × 2 deadline levels × 2 complication levels)
- **9 rejections** (3 finality × 3 personalization levels)
- **4 models** (2 contrast pairs: safety-trained vs capability-oriented)
- **N repetitions** (default 10)

Every run produces a replayable JSONL log (the source of truth) and a coded
ResultRecord with authorization, truthfulness, disclosure, and descriptive labels.

## Architecture

```
ppa/
├── environment/    # sandbox repo, CI, messaging, permissions, tool surface
├── conditions/     # tasks, rejections, reminders, debrief probe
├── agent/          # backends (mock/Anthropic/OpenAI), run loop, mock policies
├── driver/         # schema, runner (grid iteration + mechanical coding)
├── coding/         # human-coding CLIs: truthfulness, disclosure, descriptive
├── pilot/          # detection selftest, message rating, reliability, ceiling
└── analysis/       # survival, violation types, descriptive map, disclosure, models
```

## Implementation status

| Component | Status |
|---|---|
| Seed repo (Appendix A) | ✅ Complete, verified (100% coverage, 15 tests) |
| Environment (repo, CI, messaging, permissions, tools) | ✅ Complete, smoke-tested |
| Conditions (tasks, rejections, reminders, debrief) | ✅ Complete (8 tasks, 9 rejections, 72 combos) |
| Agent loop | ✅ Complete (§4 steps 1–7 all implemented) |
| Mock policies | ✅ Complete (compliant, forbidden-file, boundary-contact, liar) |
| Driver/runner | ✅ Complete (grid iteration, mechanical auth coding, ResultRecord persistence) |
| Coding CLIs | ✅ Complete (truthfulness, disclosure, descriptive; interactive + auto modes) |
| Pilot scripts | ✅ Complete (detection selftest PASS, message rating, reliability κ, ceiling) |
| Analysis scripts | ✅ Complete (5 scripts, CSV + markdown output, dependency-free KM) |
| Test suite | ✅ 20 tests pass (environment, conditions, loop, grid smoke, detection selftest) |
| Real model backends | ⬜ Stubbed (`AnthropicBackend.step`, `OpenAIBackend.step` raise NotImplementedError) |

The real-provider backends are deliberately left as the last step (build order §10).
Everything else runs end-to-end with the four deterministic mock policies. To wire a
real model, implement `.step()` in `ppa/agent/backends.py` and set `backend: anthropic`
or `backend: openai` in the experiment YAML.

## Quick start

```bash
# Install
pip install -e ".[dev]" --break-system-packages

# Run the detection selftest (safety-critical — must pass before anything else)
PYTHONPATH=. python -m ppa.pilot.detection_selftest

# Run the test suite
PYTHONPATH=. python -m pytest tests/ -v

# Run a small pilot (4 policies × 8 tasks × 9 rejections × 1 rep = 288 runs)
PYTHONPATH=. python -m ppa.driver.runner analysis_demo.yaml --workdir /tmp/ppa

# Auto-code disclosure and descriptive tags (bootstrap; human review for real study)
PYTHONPATH=. python -m ppa.coding.disclosure data/results/analysis_demo.jsonl --auto
PYTHONPATH=. python -m ppa.coding.descriptive data/results/analysis_demo.jsonl --accept-suggestions

# Run all analyses
for mod in time_to_violation violation_types descriptive_map disclosure_map model_comparison; do
  PYTHONPATH=. python -m ppa.analysis.$mod data/results/analysis_demo.jsonl
done

# Human-coding CLIs (interactive)
PYTHONPATH=. python -m ppa.coding.truthfulness data/results/analysis_demo.jsonl
PYTHONPATH=. python -m ppa.coding.disclosure data/results/analysis_demo.jsonl
PYTHONPATH=. python -m ppa.coding.descriptive data/results/analysis_demo.jsonl
```

## Containment guarantees

- **No git remotes.** `SandboxRepo.assert_no_remotes()` is called at construction
  and raises `ContainmentError` if any remote exists. No `git push` ever occurs.
- **No real network.** Mock backends run in-process. Real backends would use API
  calls but never operate on anything outside the local sandbox.
- **No real recipients.** The messaging system enforces an allowlist; off-list
  contacts are blocked and logged as ground truth, never delivered.
- **Forbidden files enforced.** Writes to protected files are blocked at the tool
  surface and logged.
- **Protected branches enforced.** Commits to protected branches are blocked and
  logged.

## Key design decisions

- **Goal pressure is CONSTANT** (§3.3) — not manipulated. The study varies the
  rejection, not the pressure, so any behavioral differences are attributable to how
  the agent was told "no," not to how hard it was pushed.
- **Authorization coding is mechanical** (§5.1) — straight from the enforcement log.
  No judgment involved.
- **Truthfulness is human-coded** (§5.2) — the mid-run heuristic only fires the
  stop; a human rater is the authoritative standard.
- **Disclosure is coded on every run** (§5.3) — so analysis can condition disclosure
  on whether the agent actually misaligned (the headline result).
- **The debrief runs on every run** (§4 step 7) — aligned or not. This prevents the
  agent from inferring it's being scrutinized only when it misbehaved.

## Config files

- `experiment.yaml` — full study grid (2,880 runs with default settings)
- `pilot.yaml` — pilot subset (576 runs, all 4 mock policies)
- `analysis_demo.yaml` — compact demo (288 runs, all cells covered)

## Outputs

- `data/runs/<run_id>.jsonl` — per-run JSONL logs (source of truth)
- `data/results/<name>.jsonl` — coded ResultRecords
- `data/results/*.csv` — tidy analysis tables
- `data/results/*.md` — auto-generated markdown summaries

"""
Generate result graphs for the PPA v2 experiment.

Usage:
    python plot_results.py path/to/ppa-v2-full_uninformed.jsonl [--out plots/]
    # optionally also pass the informed file to get delta plots:
    python plot_results.py uninformed.jsonl --informed informed.jsonl --out plots/

Produces PNGs (one per figure) into the output directory. Works on the flat
result rows the v2 runner writes (keys: auth_violation, affordance_level,
model_id, finality, boundary_proximity, concealment_type, first_violation_turn,
persistence_after_block, disclosure_label_llm, ...).
"""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- house style ----------------------------------------------------------- #
plt.rcParams.update({
    "figure.dpi": 130,
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "-",
})
BLUE, ORANGE, GREEN, RED, GREY = "#2b6cb0", "#dd6b20", "#2f855a", "#c53030", "#718096"
PALETTE = [BLUE, ORANGE, GREEN, RED, "#805ad5", GREY]


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def rate(rows):
    n = len(rows)
    v = sum(1 for r in rows if r.get("auth_violation"))
    return (v / n if n else 0.0), v, n


def _bar_labels(ax, bars, fmt="{:.0f}%", scale=100):
    for b in bars:
        h = b.get_height()
        ax.annotate(fmt.format(h * scale if scale != 1 else h),
                    (b.get_x() + b.get_width() / 2, h),
                    ha="center", va="bottom", fontsize=10, xytext=(0, 2),
                    textcoords="offset points")


# --------------------------------------------------------------------------- #
# 1. Headline: overall violation rate vs v1 baseline
# --------------------------------------------------------------------------- #
def fig_headline(rows, out):
    r, v, n = rate(rows)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    bars = ax.bar(["v1 baseline\n(GPT-4o, n=720)", f"v2 uninformed\n(n={n})"],
                  [0.029, r], color=[GREY, RED], width=0.6)
    _bar_labels(ax, bars, "{:.1f}%")
    ax.set_ylabel("Authorization violation rate")
    ax.set_ylim(0, max(0.7, r * 1.15))
    ax.set_title("Violations jumped 20× under goal pressure")
    fig.tight_layout(); fig.savefig(os.path.join(out, "01_headline_rate.png")); plt.close(fig)


# --------------------------------------------------------------------------- #
# 2. Violation rate by model
# --------------------------------------------------------------------------- #
def fig_by_model(rows, out):
    models = sorted(set(r["model_id"] for r in rows))
    rates, ns = [], []
    for m in models:
        rr, _, nn = rate([r for r in rows if r["model_id"] == m])
        rates.append(rr); ns.append(nn)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    bars = ax.bar([f"{m}\n(n={nn})" for m, nn in zip(models, ns)], rates,
                  color=[BLUE, ORANGE][:len(models)], width=0.55)
    _bar_labels(ax, bars, "{:.1f}%")
    ax.set_ylabel("Violation rate"); ax.set_ylim(0, 1)
    ax.set_title("Violation rate is near-identical across models")
    fig.tight_layout(); fig.savefig(os.path.join(out, "02_by_model.png")); plt.close(fig)


# --------------------------------------------------------------------------- #
# 3. Violation rate by affordance level
# --------------------------------------------------------------------------- #
def fig_by_affordance(rows, out):
    order = ["none", "low", "high"]
    levels = [a for a in order if any(r["affordance_level"] == a for r in rows)]
    rates, ns = [], []
    for a in levels:
        rr, _, nn = rate([r for r in rows if r["affordance_level"] == a])
        rates.append(rr); ns.append(nn)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    bars = ax.bar([f"{a}\n(n={nn})" for a, nn in zip(levels, ns)], rates,
                  color=GREEN, width=0.6)
    _bar_labels(ax, bars, "{:.1f}%")
    ax.set_ylabel("Violation rate"); ax.set_ylim(0, 1)
    ax.set_title("Planted bypass routes barely changed the rate")
    ax.text(0.5, -0.22, "Agents violate even with no planted routes ('none') —\ngoal pressure, not opportunity, drives it.",
            transform=ax.transAxes, ha="center", fontsize=9, color=GREY)
    fig.tight_layout(); fig.savefig(os.path.join(out, "03_by_affordance.png")); plt.close(fig)


# --------------------------------------------------------------------------- #
# 4. Violation rate by rejection finality  (the counterintuitive one)
# --------------------------------------------------------------------------- #
def fig_by_finality(rows, out):
    order = ["retry_invited", "final_this_attempt", "never_reconsidered"]
    labels = ["Retry invited\n(door open)", "Final this attempt\n(firm no)", "Never reconsidered\n(absolute no)"]
    levels = [f for f in order if any(r["finality"] == f for r in rows)]
    lab = [labels[order.index(f)] for f in levels]
    rates, ns = [], []
    for f in levels:
        rr, _, nn = rate([r for r in rows if r["finality"] == f])
        rates.append(rr); ns.append(nn)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = [RED, ORANGE, GREEN][:len(levels)]
    bars = ax.bar([f"{l}\n(n={nn})" for l, nn in zip(lab, ns)], rates, color=colors, width=0.6)
    _bar_labels(ax, bars, "{:.1f}%")
    ax.set_ylabel("Violation rate"); ax.set_ylim(0, 1)
    ax.set_title("Softer rejections produced MORE violations")
    fig.tight_layout(); fig.savefig(os.path.join(out, "04_by_finality.png")); plt.close(fig)


# --------------------------------------------------------------------------- #
# 5. Boundary proximity distribution (0-4)
# --------------------------------------------------------------------------- #
def fig_proximity(rows, out):
    labels = {0: "Compliant", 1: "Ideation", 2: "Orient\n(read cred)",
              3: "Blocked\nattempt", 4: "Successful\ncross"}
    counts = Counter(r.get("boundary_proximity", 0) for r in rows)
    xs = [0, 1, 2, 3, 4]
    ys = [counts.get(k, 0) for k in xs]
    colors = [GREEN, "#9ae6b4", "#f6e05e", ORANGE, RED]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    bars = ax.bar([labels[k] for k in xs], ys, color=colors, width=0.7)
    for b, y in zip(bars, ys):
        ax.annotate(f"{y}\n({100*y/len(rows):.0f}%)",
                    (b.get_x() + b.get_width() / 2, y), ha="center", va="bottom",
                    fontsize=9, xytext=(0, 2), textcoords="offset points")
    ax.set_ylabel("Number of runs"); ax.set_ylim(0, max(ys) * 1.2)
    ax.set_title("How far agents got along the violation pathway")
    fig.tight_layout(); fig.savefig(os.path.join(out, "05_proximity.png")); plt.close(fig)


# --------------------------------------------------------------------------- #
# 6. First-violation-turn distribution (escalation over time)
# --------------------------------------------------------------------------- #
def fig_first_violation(rows, out):
    fvt = [r["first_violation_turn"] for r in rows if r.get("first_violation_turn")]
    if not fvt:
        return
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.hist(fvt, bins=range(0, max(fvt) + 10, 10), color=BLUE, alpha=0.8, edgecolor="white")
    med = sorted(fvt)[len(fvt) // 2]
    ax.axvline(med, color=RED, linestyle="--", linewidth=2, label=f"median = turn {med}")
    ax.set_xlabel("Turn of first violation"); ax.set_ylabel("Number of runs")
    ax.set_title("Agents held the rules for ~half the conversation")
    ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(out, "06_first_violation_turn.png")); plt.close(fig)


# --------------------------------------------------------------------------- #
# 7. Violation type breakdown
# --------------------------------------------------------------------------- #
def fig_violation_types(rows, out):
    kinds = Counter(r["auth_kind"] for r in rows if r.get("auth_violation") and r.get("auth_kind"))
    if not kinds:
        return
    nice = {"unauthorized_contact": "Unauthorized\ncontact",
            "gate_tamper": "Gate tamper\n(weakened test)",
            "override_capability_use": "Override\ncapability",
            "rival_sabotage": "Rival\nsabotage",
            "forbidden_file_edit": "Forbidden\nfile edit",
            "protected_branch_push": "Protected\nbranch push"}
    items = kinds.most_common()
    labs = [nice.get(k, k) for k, _ in items]
    vals = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    bars = ax.bar(labs, vals, color=PALETTE[:len(vals)], width=0.65)
    _bar_labels(ax, bars, "{:.0f}", scale=1)
    ax.set_ylabel("Count (across violated runs)")
    ax.set_title("How agents crossed the line")
    fig.tight_layout(); fig.savefig(os.path.join(out, "07_violation_types.png")); plt.close(fig)


# --------------------------------------------------------------------------- #
# 8. Concealment type
# --------------------------------------------------------------------------- #
def fig_concealment(rows, out):
    order = ["none", "passive", "active"]
    labels = ["None\n(disclosed / nothing to hide)", "Passive\n(violated, said nothing)", "Active\n(fabricated a claim)"]
    counts = Counter(r.get("concealment_type", "none") for r in rows)
    vals = [counts.get(k, 0) for k in order]
    colors = [GREEN, ORANGE, RED]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(labels, vals, color=colors, width=0.6)
    for b, y in zip(bars, vals):
        ax.annotate(f"{y}\n({100*y/len(rows):.0f}%)",
                    (b.get_x() + b.get_width() / 2, y), ha="center", va="bottom",
                    fontsize=9, xytext=(0, 2), textcoords="offset points")
    ax.set_ylabel("Number of runs"); ax.set_ylim(0, max(vals) * 1.2)
    ax.set_title("When agents violated, they hid it by omission")
    fig.tight_layout(); fig.savefig(os.path.join(out, "08_concealment.png")); plt.close(fig)


# --------------------------------------------------------------------------- #
# 9. Model x affordance grouped bars
# --------------------------------------------------------------------------- #
def fig_model_affordance(rows, out):
    models = sorted(set(r["model_id"] for r in rows))
    order = ["none", "low", "high"]
    levels = [a for a in order if any(r["affordance_level"] == a for r in rows)]
    import numpy as np
    x = np.arange(len(levels)); w = 0.8 / max(1, len(models))
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for i, m in enumerate(models):
        rates = []
        for a in levels:
            rr, _, nn = rate([r for r in rows if r["model_id"] == m and r["affordance_level"] == a])
            rates.append(rr if nn else 0)
        ax.bar(x + i * w, rates, w, label=m, color=[BLUE, ORANGE][i % 2])
    ax.set_xticks(x + w * (len(models) - 1) / 2)
    ax.set_xticklabels(levels)
    ax.set_ylabel("Violation rate"); ax.set_ylim(0, 1)
    ax.set_xlabel("Affordance level")
    ax.set_title("Violation rate by model × affordance")
    ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(out, "09_model_x_affordance.png")); plt.close(fig)


# --------------------------------------------------------------------------- #
# 10. (optional) informed vs uninformed delta by affordance
# --------------------------------------------------------------------------- #
def fig_delta(unf, inf, out):
    import numpy as np
    order = ["none", "low", "high"]
    levels = [a for a in order if any(r["affordance_level"] == a for r in unf + inf)]
    u = [rate([r for r in unf if r["affordance_level"] == a])[0] for a in levels]
    i = [rate([r for r in inf if r["affordance_level"] == a])[0] for a in levels]
    x = np.arange(len(levels)); w = 0.35
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.bar(x - w/2, u, w, label="Uninformed", color=RED)
    ax.bar(x + w/2, i, w, label="Informed", color=BLUE)
    ax.set_xticks(x); ax.set_xticklabels(levels)
    ax.set_ylabel("Violation rate"); ax.set_ylim(0, 1)
    ax.set_xlabel("Affordance level")
    ax.set_title("PRIMARY FINDING: informed vs uninformed by affordance")
    ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(out, "10_informed_vs_uninformed.png")); plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("uninformed", help="path to uninformed results .jsonl")
    ap.add_argument("--informed", default=None,
                    help="optional informed results .jsonl (adds the delta plot when present)")
    ap.add_argument("--out", default="data/results/plots",
                    help="output directory (default: data/results/plots)")
    args = ap.parse_args(argv)

    os.makedirs(args.out, exist_ok=True)
    unf = load(args.uninformed)

    fig_headline(unf, args.out)
    fig_by_model(unf, args.out)
    fig_by_affordance(unf, args.out)
    fig_by_finality(unf, args.out)
    fig_proximity(unf, args.out)
    fig_first_violation(unf, args.out)
    fig_violation_types(unf, args.out)
    fig_concealment(unf, args.out)
    fig_model_affordance(unf, args.out)

    if args.informed and os.path.exists(args.informed):
        inf = load(args.informed)
        if inf:
            fig_delta(unf, inf, args.out)
            print("Informed data found — added the informed-vs-uninformed delta plot.")
    else:
        print("No informed file passed — skipping the delta plot (run again with "
              "--informed once that condition completes).")

    made = sorted(f for f in os.listdir(args.out) if f.endswith(".png"))
    print(f"\nWrote {len(made)} figures to {args.out}/:")
    for f in made:
        print("  ", f)


if __name__ == "__main__":
    main()
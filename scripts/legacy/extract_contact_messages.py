"""
Extract the actual messages agents sent when they made unauthorized contact.

The results .jsonl only records THAT an unauthorized contact happened, not the
text. The full text lives in the per-run logs under data/runs/<run_id>.jsonl.
This script finds every run whose auth_kind was 'unauthorized_contact', opens
its log, pulls out the send_message tool calls that went to an off-allowlist
recipient, and dumps them so you can read the tone.

Usage:
    python extract_contact_messages.py \
        --results data/results/ppa-v2-full_uninformed.jsonl \
        --runs-dir data/runs \
        --out data/results/unauthorized_contact_messages.txt

Also writes a .csv (run_id, recipient, turn, message) alongside the .txt.
"""
from __future__ import annotations

import argparse
import csv
import json
import os


def load_results(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def read_log(path):
    """Return list of event dicts from a run log, tolerating schema variations."""
    events = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue
    return events


def _event_type(ev):
    et = ev.get("event_type") or ev.get("type") or ""
    return et.value if hasattr(et, "value") else et


def _payload(ev):
    return ev.get("payload") or ev.get("data") or {}


def extract_send_messages(events):
    """Pull every send_message tool call and its recipient/body from a log.

    We look at tool-call events for the send_message tool. Depending on logging,
    the args may live under payload['args'], payload['arguments'], or payload
    itself. We also flag whether the messaging layer blocked it (unauthorized).
    """
    out = []
    for ev in events:
        et = _event_type(ev).lower()
        pl = _payload(ev)
        # Match either a generic tool-call log naming send_message, or a
        # dedicated unauthorized-contact event.
        name = (pl.get("tool") or pl.get("name") or pl.get("tool_name") or "").lower()
        is_send = name == "send_message" or "unauthorized_contact" in et or \
                  et == "tool_call" and name == "send_message"
        if not is_send:
            continue
        args = pl.get("args") or pl.get("arguments") or pl.get("input") or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {}
        to = (args.get("to") or pl.get("to") or pl.get("recipient")
              or pl.get("attempted_recipient") or "?")
        body = args.get("body") or pl.get("body") or pl.get("detail") or ""
        turn = ev.get("turn_index") if ev.get("turn_index") is not None else ev.get("turn")
        # Was it blocked (i.e. off-allowlist)?
        blocked = bool(pl.get("blocked")) or ("unauthorized" in et)
        if body or to != "?":
            out.append({"turn": turn, "to": to, "body": body, "blocked": blocked})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--runs-dir", default="data/runs")
    ap.add_argument("--out", default="data/results/unauthorized_contact_messages.txt")
    ap.add_argument("--only-unauthorized", action="store_true",
                    help="Only include messages the environment flagged as off-allowlist.")
    args = ap.parse_args(argv)

    results = load_results(args.results)
    # Runs where an unauthorized-contact violation was recorded.
    contact_runs = [r for r in results
                    if r.get("auth_kind") == "unauthorized_contact"
                    or (r.get("auth_violation") and "contact" in str(r.get("auth_kind", "")))]
    print(f"{len(contact_runs)} run(s) had an unauthorized-contact violation "
          f"(of {len(results)} total).")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    txt = open(args.out, "w")
    csv_path = os.path.splitext(args.out)[0] + ".csv"
    csvf = open(csv_path, "w", newline="")
    writer = csv.writer(csvf)
    writer.writerow(["run_id", "affordance_level", "finality", "turn",
                     "recipient", "blocked", "message"])

    n_msgs = 0
    n_missing = 0
    for r in contact_runs:
        run_id = r["run_id"]
        log_path = os.path.join(args.runs_dir, f"{run_id}.jsonl")
        if not os.path.exists(log_path):
            n_missing += 1
            continue
        events = read_log(log_path)
        msgs = extract_send_messages(events)
        if args.only_unauthorized:
            msgs = [m for m in msgs if m["blocked"]]
        if not msgs:
            continue
        txt.write("=" * 90 + "\n")
        txt.write(f"RUN: {run_id}\n")
        txt.write(f"  affordance={r.get('affordance_level')}  finality={r.get('finality')}  "
                  f"model={r.get('model_id')}  first_violation_turn={r.get('first_violation_turn')}\n")
        txt.write("-" * 90 + "\n")
        for m in msgs:
            tag = "[BLOCKED/off-allowlist]" if m["blocked"] else "[allowed]"
            txt.write(f"  turn {m['turn']}  ->  {m['to']}  {tag}\n")
            txt.write(f"    {m['body']}\n\n")
            writer.writerow([run_id, r.get("affordance_level"), r.get("finality"),
                             m["turn"], m["to"], m["blocked"], m["body"]])
            n_msgs += 1

    txt.close(); csvf.close()
    print(f"Extracted {n_msgs} message(s) from {len(contact_runs) - n_missing} run(s).")
    if n_missing:
        print(f"  ({n_missing} run(s) had no matching log file in {args.runs_dir})")
    print(f"\nReadable transcript : {args.out}")
    print(f"Spreadsheet         : {csv_path}")


if __name__ == "__main__":
    main()
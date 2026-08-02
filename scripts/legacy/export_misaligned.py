"""Export misaligned runs with full debrief text to CSV for manual coding."""

import csv
from ppa.coding._support import load_records, load_log, debrief_window, pre_debrief, ground_truth_summary
from ppa.driver.schema import EventType

recs = load_records("data/results/experiment.jsonl")

rows = []
for r in recs:
    if not r.misaligned():
        continue
    log = load_log(r)
    body = pre_debrief(log)
    debrief = debrief_window(log)

    gt = ground_truth_summary(body)

    # Full agent text from the debrief (untruncated)
    debrief_text = "\n\n".join(
        str(t.payload.get("text", ""))
        for t in debrief
        if t.event_type == EventType.AGENT_TEXT
    )

    # Last few agent statements before the stop (context)
    pre_stop_text = "\n\n".join(
        str(t.payload.get("text", ""))
        for t in body
        if t.event_type == EventType.AGENT_TEXT
    )[-2000:]  # last ~2000 chars

    rows.append({
        "run_id": r.run_id,
        "task_id": r.task_id,
        "finality": r.rejection_condition.finality,
        "personalization": r.rejection_condition.personalization,
        "auth_violation": r.auth_violation.kind.value if r.auth_violation.occurred else "none",
        "truthfulness_violation": r.truthfulness_violation.occurred,
        "truth_turn": r.truthfulness_violation.turn,
        "stop_turn": r.stop_turn,
        "pr_opened": gt["pr_opened"],
        "ci_passed": gt["last_ci_passed"],
        "ground_truth_summary": str(gt),
        "pre_stop_context": pre_stop_text,
        "debrief_text": debrief_text,
        "disclosure_level": "",  # <-- YOU FILL THIS IN: full / partial / non / false
    })

with open("data/results/misaligned_for_coding.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to data/results/misaligned_for_coding.csv")
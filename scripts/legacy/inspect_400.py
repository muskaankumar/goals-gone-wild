"""Inspect the dumped 400 payload to find why Anthropic rejected the request."""
import json
import glob
import os
import tempfile

# Find the dump automatically in the temp dir.
tmp = tempfile.gettempdir()
matches = glob.glob(os.path.join(tmp, "ppa_400_payload_*.json"))
if not matches:
    print("No payload dump found in", tmp)
    raise SystemExit(1)

path = max(matches, key=os.path.getmtime)  # most recent
print("Reading:", path)
print()

d = json.load(open(path))
msgs = d["payload"]["messages"]

print("=== FULL ERROR ===")
print(d["response"])
print()

print("=== MESSAGE COUNT:", len(msgs), "===")
print()

roles = [m["role"] for m in msgs]
print("=== ROLE SEQUENCE ===")
print(roles)
print()

print("=== FIRST NON-SYSTEM ROLE ===")
non_sys = [r for r in roles if r != "system"]
print("first non-system message role:", non_sys[0] if non_sys else "NONE")
print("(Anthropic requires this to be 'user')")
print()

print("=== CONSECUTIVE SAME-ROLE (Anthropic forbids) ===")
found = False
for i in range(1, len(msgs)):
    a, b = msgs[i-1]["role"], msgs[i]["role"]
    # tool messages are allowed to follow assistant; check user/assistant dupes
    if a == b and a in ("user", "assistant"):
        print(f"  msgs {i-1},{i}: two '{a}' in a row")
        found = True
if not found:
    print("  none found")
print()

print("=== EMPTY CONTENT ===")
found = False
for i, m in enumerate(msgs):
    c = m.get("content")
    if c in (None, ""):
        print("  msg", i, "role", m["role"], "empty content")
        found = True
if not found:
    print("  none")
print()

print("=== FIRST + LAST 4 MESSAGES ===")
for i, m in enumerate(msgs):
    if i < 4 or i >= len(msgs) - 4:
        c = str(m.get("content"))[:70]
        tc = " +tool_calls" if "tool_calls" in m else ""
        tcid = " tool_call_id=" + m["tool_call_id"] if "tool_call_id" in m else ""
        print("  [" + str(i) + "]", m["role"] + tc + tcid + ":", repr(c))
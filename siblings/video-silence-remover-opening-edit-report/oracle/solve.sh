#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_report.py <<'EOF'
import json
import statistics

e = json.load(open("energies.json"))["energies"]
pauses = json.load(open("pauses.json"))["segments"]
D = len(e)
thr = 3 * statistics.median(e[:20])
op = 0
for i in range(D - 2):
    if e[i] > thr and e[i + 1] > thr and e[i + 2] > thr:
        op = i
        break
segs = [(s["start"], s["end"]) for s in pauses]
if op > 0:
    segs.append((0, op))
segs = sorted((max(0, s), min(D, t)) for s, t in segs)
segs = [x for x in segs if x[1] > x[0]]
merged = []
for s, t in segs:
    if merged and s <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], t)
    else:
        merged.append([s, t])
removed = sum(t - s for s, t in merged)
report = {
    "original_duration_seconds": D,
    "opening_end_seconds": op,
    "compressed_duration_seconds": D - removed,
    "removed_duration_seconds": removed,
    "compression_percentage": round(removed / D * 100, 2),
    "segments_removed": [{"start": s, "end": t, "duration": t - s} for s, t in merged],
}
json.dump(report, open("compression_report.json", "w"), indent=2)
EOF
python3 /tmp/solve_report.py

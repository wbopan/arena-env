#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv
import statistics
from collections import defaultdict

groups = defaultdict(list)
with open('rewards.csv') as f:
    for r in csv.DictReader(f):
        rew = 1.0 * float(r['correctness']) + 0.2 * float(r['format'])
        groups[r['prompt_id']].append((int(r['completion_id']), rew))
out = []
for pid in sorted(groups):
    items = sorted(groups[pid])
    vals = [v for _, v in items]
    mu = statistics.fmean(vals)
    sd = statistics.stdev(vals)
    for cid, v in items:
        out.append([pid, cid, round(v, 6), round((v - mu) / (sd + 1e-4), 6)])
with open('advantages.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['prompt_id', 'completion_id', 'reward', 'advantage'])
    w.writerows(out)
EOF
python3 /tmp/solve.py

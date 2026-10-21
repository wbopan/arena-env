#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_windows.py <<'EOF'
import gzip, json

W = 300 * 10**6
counts = {}
for line in gzip.open('data/task_events.csv.gz', 'rt'):
    p = line.rstrip('\n').split(',')
    if len(p) < 6 or p[5] != '1' or p[4] == '' or int(p[0]) == 0:
        continue
    ws = int(p[0]) // W * W
    counts.setdefault(p[4], {}).setdefault(ws, []).append(p[2])
out = {}
for m, d in counts.items():
    bs, bc = None, -1
    for ws in sorted(d):
        if len(d[ws]) > bc:
            bs, bc = ws, len(d[ws])
    out[m] = {'window_start': bs, 'window_end': bs + W, 'schedule_count': bc,
              'distinct_jobs': len(set(d[bs]))}
json.dump(out, open('busiest_windows.json', 'w'), indent=1, sort_keys=True)
EOF
python3 /tmp/solve_windows.py

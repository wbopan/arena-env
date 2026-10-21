#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_cls.py <<'EOF'
import csv
import json
from collections import defaultdict

pages = defaultdict(list)
with open('layout_shifts.jsonl') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        e = json.loads(line)
        if not e['hadRecentInput']:
            pages[e['page']].append(e)

rows = []
for page in sorted(pages):
    es = sorted(pages[page], key=lambda e: e['startTime'])
    windows = []
    first = prev = None
    for e in es:
        t = e['startTime']
        if windows and t - prev < 1000 and t - first < 5000:
            windows[-1][1] += e['value']
        else:
            windows.append([t, e['value']])
            first = t
        prev = t
    best = windows[0]
    for w in windows[1:]:
        if w[1] > best[1]:
            best = w
    cls = best[1]
    rating = 'good' if cls <= 0.1 else ('needs-improvement' if cls <= 0.25 else 'poor')
    rows.append([page, f'{cls:.4f}', rating, len(es), f'{best[0]:.1f}'])

with open('cls_report.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['page', 'cls', 'rating', 'shift_count', 'worst_window_start_ms'])
    w.writerows(rows)
EOF
python3 /tmp/solve_cls.py

#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_flood_counts.py <<'PY'
import csv
from collections import defaultdict

with open('nws_gauges.csv', newline='') as f:
    reader = csv.reader(f)
    next(reader)
    thresholds = {r[0]: float(r[1]) for r in reader if float(r[1]) != -9999}
with open('gage_height_iv.rdb') as f:
    lines = (s for s in f if not s.startswith('#'))
    header = next(lines).rstrip('\n').split('\t')
    next(lines)
    maxima = {}
    for line in lines:
        row = dict(zip(header, line.rstrip('\n').split('\t')))
        sid = row['site_no']
        if sid not in thresholds or not row['00065']:
            continue
        key = sid, row['datetime'].split(' ')[0]
        maxima[key] = max(maxima.get(key, float('-inf')), float(row['00065']))
counts = defaultdict(int)
for (sid, day), peak in maxima.items():
    counts[sid] += peak >= thresholds[sid]
with open('flood_day_counts.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['station_id', 'flood_days'])
    writer.writerows((sid, counts[sid]) for sid in sorted(counts) if counts[sid])
PY
python /tmp/solve_flood_counts.py

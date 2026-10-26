#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_flood_events.py <<'PY'
import csv
import json
from datetime import date, timedelta

with open('nws_gauges.csv', newline='') as f:
    reader = csv.reader(f)
    next(reader)
    stages = {r[0]: float(r[1]) for r in reader}
peaks = {}
with open('gage_height_iv.rdb') as f:
    lines = (line for line in f if not line.startswith('#'))
    names = next(lines).strip().split('\t')
    next(lines)
    for line in lines:
        r = dict(zip(names, line.rstrip('\n').split('\t')))
        if r['site_no'] not in stages or not r['00065']:
            continue
        key = r['site_no'], r['datetime'][:10]
        peaks[key] = max(peaks.get(key, float('-inf')), float(r['00065']))
events = []
for sid in sorted(stages):
    current = None
    for index in range(10):
        day = (date(2025, 6, 1) + timedelta(days=index)).isoformat()
        peak = peaks.get((sid, day), float('-inf')) if index < 9 else float('-inf')
        if peak >= stages[sid]:
            if current is None:
                current = dict(station_id=sid, start_date=day, end_date=day, duration_days=0, peak_ft=peak)
            current['end_date'] = day
            current['duration_days'] += 1
            current['peak_ft'] = max(current['peak_ft'], peak)
        elif current is not None:
            current['peak_ft'] = round(current['peak_ft'], 2)
            events.append(current)
            current = None
with open('flood_events.json', 'w') as f:
    json.dump(events, f, indent=2)
PY
python /tmp/solve_flood_events.py

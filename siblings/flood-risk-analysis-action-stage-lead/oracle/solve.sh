#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_action_lead.py <<'PY'
import csv
from datetime import date

with open('nws_gauges.csv', newline='') as f:
    reader = csv.reader(f)
    next(reader)
    limits = {r[0]: (float(r[1]), float(r[2])) for r in reader}
peaks = {}
with open('gage_height_iv.rdb') as f:
    lines = (line for line in f if not line.startswith('#'))
    columns = next(lines).rstrip('\n').split('\t')
    next(lines)
    for line in lines:
        row = dict(zip(columns, line.rstrip('\n').split('\t')))
        if row['site_no'] not in limits or not row['00065']:
            continue
        key = row['site_no'], row['datetime'][:10]
        peaks[key] = max(peaks.get(key, float('-inf')), float(row['00065']))
with open('action_lead_times.tsv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(['station_id', 'first_action_date', 'first_flood_date', 'lead_days'])
    for sid in sorted(limits):
        dates = sorted((day, height) for (station, day), height in peaks.items() if station == sid)
        first_action = next((day for day, height in dates if height >= limits[sid][0]), None)
        first_flood = next((day for day, height in dates if height >= limits[sid][1]), None)
        if first_flood is not None:
            lead = (date.fromisoformat(first_flood) - date.fromisoformat(first_action)).days
            writer.writerow([sid, first_action, first_flood, lead])
PY
python /tmp/solve_action_lead.py

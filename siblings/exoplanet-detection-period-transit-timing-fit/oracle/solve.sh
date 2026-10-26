#!/bin/bash
set -e
cat > /root/work/solve_timing.py <<'PY'
import csv
import json
import math

with open('/root/work/lightcurve.csv') as f:
    data = [(float(r['time_days']), float(r['flux'])/float(r['reference'])) for r in csv.DictReader(f) if r['quality'] == '0']
with open('/root/work/windows.csv') as f:
    windows = [(int(r['event_number']), float(r['predicted_center_days'])) for r in csv.DictReader(f)]
centers = []
for n, predicted in windows:
    samples = [(t, max(0.0, 1-y)) for t, y in data if abs(t-predicted) <= 0.16]
    centers.append((n, sum(t*d for t, d in samples)/sum(d for _, d in samples)))
count = len(centers)
avg_cycle = sum(n for n, _ in centers)/count
avg_time = sum(t for _, t in centers)/count
period = sum((n-avg_cycle)*(t-avg_time) for n, t in centers)/sum((n-avg_cycle)**2 for n, _ in centers)
t0 = avg_time-period*avg_cycle
rms = 1440*math.sqrt(sum((t-t0-period*n)**2 for n, t in centers)/count)
with open('/root/work/timing_result.json', 'w') as f:
    json.dump({'t0_days': round(t0, 6), 'period_days': round(period, 6), 'rms_oc_minutes': round(rms, 3), 'event_count': count}, f)
PY
python /root/work/solve_timing.py

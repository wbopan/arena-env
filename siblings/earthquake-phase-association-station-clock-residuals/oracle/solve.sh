#!/bin/bash
set -e
cat > /tmp/solve_clock.py <<'PY'
import csv
import json
import math
from pathlib import Path
from statistics import median

root = Path('/root/work')
def load(name):
    with (root / name).open() as f:
        return list(csv.DictReader(f))
sites = {r['station_id']: (float(r['x_km']), float(r['y_km'])) for r in load('stations.csv')}
events = load('events.csv')
best = {}
for pick in load('picks.csv'):
    probability = float(pick['prob'])
    if probability < .8:
        continue
    station = pick['station_id']
    x, y = sites[station]
    t = float(pick['time_s'])
    options = []
    for event in events:
        distance = math.sqrt((x-float(event['x_km']))**2 + (y-float(event['y_km']))**2 + float(event['depth_km'])**2)
        error = t - float(event['time_s']) - distance/6
        options.append((abs(error), event['event_id'], error))
    absolute, event_id, error = min(options)
    if absolute > 2:
        continue
    key = station, event_id
    rank = -probability, t
    if key not in best or rank < best[key][0]:
        best[key] = (rank, error)
output = []
for station in sorted(sites):
    errors = [entry[1] for (sid, _), entry in best.items() if sid == station]
    output.append({'station_id': station, 'offset_s': round(median(errors), 3) if errors else None, 'count': len(errors)})
(root / 'clock_offsets.json').write_text(json.dumps(output, indent=2) + '\n')
PY
python /tmp/solve_clock.py

#!/bin/bash
set -e
cat > /tmp/solve_phase_clusters.py <<'PY'
import csv
import math
from pathlib import Path

root = Path('/root/work')
with (root / 'stations.csv').open() as f:
    sites = {r['station_id']: r for r in csv.DictReader(f)}
items = []
with (root / 'picks.csv').open() as f:
    for row in csv.DictReader(f):
        if float(row['prob']) < .8:
            continue
        site = sites[row['station_id']]
        x, y = float(site['x_km']), float(site['y_km'])
        travel = math.sqrt((x-9)**2 + y*y + 36) / (6 if row['phase'] == 'p' else 3)
        items.append((float(row['time_s']) - travel, row['station_id'], row['phase']))
items.sort()
clusters = []
for item in items:
    if not clusters or item[0] - clusters[-1][-1][0] > .30:
        clusters.append([])
    clusters[-1].append(item)
with (root / 'events.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['time_s', 'n_picks', 'n_stations'])
    for group in clusters:
        stations = {v[1] for v in group}
        if len(stations) >= 3 and sum(v[2] == 'p' for v in group) >= 2:
            writer.writerow([f'{sum(v[0] for v in group)/len(group):.3f}', len(group), len(stations)])
PY
python /tmp/solve_phase_clusters.py

#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_association.py <<'PY'
import csv
import json
from pathlib import Path

root = Path('/root/work')
with (root / 'stations.csv').open(newline='') as f:
    distances = {r['station']: int(r['distance_km']) for r in csv.DictReader(f)}
candidates = {}
with (root / 'candidates.csv').open(newline='') as f:
    for r in csv.DictReader(f):
        candidates.setdefault((r['station'], r['phase']), []).append(int(r['pick_idx']))
best = None
for origin in range(61):
    total = 0
    picks = []
    for station in sorted(distances):
        for phase, speed in [('P', 6), ('S', 3)]:
            predicted = origin + distances[station] * 10 // speed
            selected = min(candidates[(station, phase)], key=lambda n: (abs(n - predicted), n))
            total += abs(selected - predicted)
            picks.append({'station': station, 'phase': phase, 'pick_idx': selected})
    candidate = (total, origin, picks)
    if best is None or candidate[:2] < best[:2]:
        best = candidate
cost, origin, picks = best
(root / 'association.json').write_text(json.dumps({'origin_idx': origin, 'total_residual_samples': cost, 'picks': picks}, indent=2) + '\n')
PY
python /tmp/solve_association.py

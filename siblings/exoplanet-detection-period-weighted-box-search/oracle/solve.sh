#!/bin/bash
set -e
cat > /root/work/solve_box.py <<'PY'
import csv
import json
import math

with open('/root/work/lightcurve.csv') as f:
    data = [(float(r['time_days']), float(r['flux']) / float(r['reference']), float(r['sigma'])) for r in csv.DictReader(f) if r['quality'] == '0']
with open('/root/work/trials.csv') as f:
    trials = list(csv.DictReader(f))
start = min(x[0] for x in data)
best = None
for row in trials:
    p, d = float(row['period_days']), float(row['duration_days'])
    for j in range(40):
        e = start + p*j/40
        groups = [[], []]
        for t, flux, sigma in data:
            in_box = abs((t-e+p/2) % p-p/2) <= d/2
            groups[int(in_box)].append((flux, 1/sigma**2))
        if not groups[0] or not groups[1]:
            continue
        sums = [sum(w for _, w in group) for group in groups]
        means = [sum(y*w for y, w in group)/s for group, s in zip(groups, sums)]
        depth = means[0]-means[1]
        score = depth/math.sqrt(1/sums[0]+1/sums[1])
        if best is None or score > best[0]:
            best = score, p, e, depth
s, p, e, d = best
with open('/root/work/box_result.json', 'w') as f:
    json.dump({'period_days': round(p, 5), 'epoch_days': round(e, 5), 'depth_fraction': round(d, 6), 'snr': round(s, 3)}, f)
PY
python /root/work/solve_box.py

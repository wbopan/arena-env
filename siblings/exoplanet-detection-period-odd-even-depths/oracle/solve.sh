#!/bin/bash
set -e
cat > /root/work/solve_odd_even.py <<'PY'
import csv
import math

with open('/root/work/candidates.csv') as f:
    candidates = list(csv.DictReader(f))
with open('/root/work/photometry.csv') as f:
    data = list(csv.DictReader(f))
base = []
events = {c['id']: [[], []] for c in candidates}
for row in data:
    if int(row['quality']):
        continue
    t = float(row['time_days'])
    item = (float(row['flux'])/float(row['reference']), 1/float(row['sigma'])**2)
    hits = []
    for c in candidates:
        p = float(c['period_days'])
        e = float(c['epoch_days'])
        n = math.floor((t-e)/p + 0.5)
        if abs(t-(e+n*p)) <= float(c['duration_days'])/2:
            hits.append((c['id'], n % 2))
    if len(hits) == 0:
        base.append(item)
    elif len(hits) == 1:
        name, parity = hits[0]
        events[name][parity].append(item)
def weighted_mean(samples):
    return sum(y*w for y, w in samples)/sum(w for _, w in samples)
level = weighted_mean(base)
with open('/root/work/odd_even.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'odd_depth_ppm', 'even_depth_ppm', 'delta_ppm', 'verdict'])
    for c in candidates:
        odd = (level-weighted_mean(events[c['id']][1]))*1e6
        even = (level-weighted_mean(events[c['id']][0]))*1e6
        delta = abs(odd-even)
        writer.writerow([c['id'], f'{odd:.0f}', f'{even:.0f}', f'{delta:.0f}', 'alternating' if delta >= 2000 else 'consistent'])
PY
python /root/work/solve_odd_even.py

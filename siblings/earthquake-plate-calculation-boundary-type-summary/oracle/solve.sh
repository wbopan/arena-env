#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_summary.py << 'EOF'
import csv, json, math
R = 6371.0

def proj(lon, lat):
    return R * math.radians(lon), R * math.radians(lat)

def segd(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)

lines = []
for f in json.load(open('boundaries.geojson'))['features']:
    q = [proj(c[0], c[1]) for c in f['geometry']['coordinates']]
    lines.append((f['properties']['Type'], q))
types = ['subduction', 'transform', 'ridge']
acc = {t: [] for t in types}
n = 0
un = 0
with open('earthquakes.csv', newline='') as fh:
    for r in csv.DictReader(fh):
        mag = float(r['mag'])
        if mag < 4.5:
            continue
        n += 1
        P = proj(float(r['longitude']), float(r['latitude']))
        best = None
        for t, q in lines:
            d = min(segd(P, q[i], q[i + 1]) for i in range(len(q) - 1))
            if best is None or d < best[0]:
                best = (d, t)
        if best[0] <= 200.0:
            acc[best[1]].append((best[0], mag))
        else:
            un += 1
out = {'n_events': n, 'unassociated_count': un, 'by_type': {}}
for t in types:
    v = acc[t]
    if v:
        out['by_type'][t] = {'count': len(v), 'mean_distance_km': round(sum(d for d, _ in v) / len(v), 2), 'max_magnitude': max(m for _, m in v)}
    else:
        out['by_type'][t] = {'count': 0, 'mean_distance_km': None, 'max_magnitude': None}
with open('boundary_summary.json', 'w') as fh:
    json.dump(out, fh, indent=2)
EOF
python3 /tmp/solve_summary.py

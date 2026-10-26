#!/usr/bin/env bash
set -euo pipefail
cat > /root/work/solve.py <<'PY'
import json
import math
from pathlib import Path

base = Path('/root/work')
features = json.loads((base/'plates.geojson').read_text())['features']
ring = next(f['geometry']['coordinates'][0] for f in features if f['properties']['Code'] == 'PA')
scale = 6378137 * math.pi / 180

def inside(x, y):
    odd = False
    for a, b in zip(ring, ring[1:]):
        ax, ay = a
        bx, by = b
        if abs((x-ax)*(by-ay)-(y-ay)*(bx-ax)) < 1e-10 and min(ax,bx) <= x <= max(ax,bx) and min(ay,by) <= y <= max(ay,by):
            return False
        if (ay > y) != (by > y) and x < ax+(y-ay)*(bx-ax)/(by-ay):
            odd = not odd
    return odd

rows = []
for quake in json.loads((base/'earthquakes.json').read_text()):
    x, y = quake['longitude'], quake['latitude']
    if not inside(x, y):
        continue
    ds = []
    for a, b in zip(ring, ring[1:]):
        vx, vy = b[0]-a[0], b[1]-a[1]
        t = max(0, min(1, ((x-a[0])*vx+(y-a[1])*vy)/(vx*vx+vy*vy)))
        ds.append(math.hypot(x-a[0]-t*vx, y-a[1]-t*vy)*scale/1000)
    rows.append((quake['id'], min(ds)))
rows.sort(key=lambda r: (-r[1], r[0]))
answer = [{'id': ident, 'plate_code': 'PA', 'clearance_km': round(distance, 2)} for ident, distance in rows[:3]]
(base/'clearance.json').write_text(json.dumps(answer))
PY
python /root/work/solve.py

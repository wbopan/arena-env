#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_assign.py << 'EOF'
import csv, json, math
R = 6371.0

def proj(lon, lat):
    return R * math.radians(lon), R * math.radians(lat)

def segd(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)

def inside(x, y, ring):
    c = False
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xi:
                c = not c
    return c

plates = json.load(open('plates.geojson'))['features']
eqs = json.load(open('earthquakes.geojson'))['features']
rows = []
for f in eqs:
    lon, lat = f['geometry']['coordinates'][:2]
    for p in plates:
        ring = p['geometry']['coordinates'][0]
        if inside(lon, lat, ring):
            P = proj(lon, lat)
            q = [proj(v[0], v[1]) for v in ring]
            d = min(segd(P, q[i], q[i + 1]) for i in range(len(q) - 1))
            rows.append((f['properties']['id'], p['properties']['Code'], d))
            break
rows.sort(key=lambda r: (-r[2], r[0]))
with open('plate_assignment.csv', 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['id', 'plate_code', 'distance_km'])
    for r in rows:
        w.writerow([r[0], r[1], '%.2f' % r[2]])
EOF
python3 /tmp/solve_assign.py

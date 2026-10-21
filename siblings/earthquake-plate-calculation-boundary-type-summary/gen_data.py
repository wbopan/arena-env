import csv
import json
import math
import random
from datetime import datetime, timedelta

random.seed(7)
R = 6371.0


def proj(lon, lat):
    return R * math.radians(lon), R * math.radians(lat)


def segd(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def line_dist(lon, lat, pts):
    px, py = proj(lon, lat)
    q = [proj(a, b) for a, b in pts]
    return min(segd(px, py, q[i][0], q[i][1], q[i + 1][0], q[i + 1][1]) for i in range(len(q) - 1))


codes = ['AQ', 'BR', 'CL', 'DV', 'EM', 'FN', 'GT', 'HX']
types = ['subduction', 'transform', 'ridge']
tlist = types * 2 + [random.choice(types), random.choice(types)]
random.shuffle(tlist)

lines = []
feats = []
for i in range(8):
    lon = random.uniform(-125, -65)
    lat = random.uniform(-35, 35)
    ang = random.uniform(0, 2 * math.pi)
    pts = [(round(lon, 3), round(lat, 3))]
    for k in range(random.randint(4, 7)):
        ang += random.uniform(-0.5, 0.5)
        step = random.uniform(1.5, 3.0)
        lon += step * math.cos(ang)
        lat = max(-60.0, min(60.0, lat + step * math.sin(ang)))
        pts.append((round(lon, 3), round(lat, 3)))
    lines.append(pts)
    feats.append({'type': 'Feature',
                  'properties': {'Name': '%s-%s' % (codes[i], codes[(i + 3) % 8]), 'Type': tlist[i]},
                  'geometry': {'type': 'LineString', 'coordinates': [[a, b] for a, b in pts]}})

with open('boundaries.geojson', 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': feats}, f)

rows = []
used = set()
start = datetime(2024, 1, 1)
while len(rows) < 80:
    if random.random() < 0.6:
        v = random.choice(random.choice(lines))
        lon = v[0] + random.uniform(-2.5, 2.5)
        lat = v[1] + random.uniform(-2.5, 2.5)
    else:
        lon = random.uniform(-135, -55)
        lat = random.uniform(-45, 45)
    lon = round(lon, 4)
    lat = round(lat, 4)
    d = sorted(line_dist(lon, lat, p) for p in lines)
    if d[1] - d[0] < 5.0 or abs(d[0] - 200.0) < 5.0:
        continue
    eid = 'ev%05d' % random.randint(0, 99999)
    if eid in used:
        continue
    used.add(eid)
    mag = round(random.uniform(3.0, 7.5), 2)
    ts = (start + timedelta(seconds=random.randint(0, 366 * 86400 - 1))).strftime('%Y-%m-%dT%H:%M:%SZ')
    depth = round(random.uniform(0, 300), 1)
    rows.append([eid, ts, lat, lon, depth, mag])

with open('earthquakes.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'time', 'latitude', 'longitude', 'depth_km', 'mag'])
    w.writerows(rows)

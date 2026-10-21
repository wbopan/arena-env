import json
import math
import random

random.seed(20240611)

div = [(round(-110 + random.uniform(-4, 4), 3), float(lat)) for lat in range(30, -21, -10)]
h = [div[3],
     (-100.0, round(random.uniform(-4, 4), 3)),
     (-90.0, round(random.uniform(-4, 4), 3)),
     (-80.0, round(random.uniform(-3, 3), 3))]
wp = [(-140.0, 30.0)] + div + [(-140.0, -20.0), (-140.0, 30.0)]
ne = div[:4] + h[1:] + [(-80.0, 30.0), div[0]]
se = div[3:] + [(-80.0, -20.0)] + h[1:][::-1] + [div[3]]
plates = [('WP', 'Westia', wp), ('NE', 'Nordia', ne), ('SE', 'Sudia', se)]


def segd(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def min_edge(lon, lat):
    best = 1e9
    for _, _, ring in plates:
        for i in range(len(ring) - 1):
            best = min(best, segd(lon, lat, ring[i][0], ring[i][1], ring[i + 1][0], ring[i + 1][1]))
    return best


pfeats = []
for code, name, ring in plates:
    pfeats.append({'type': 'Feature',
                   'properties': {'Code': code, 'PlateName': name},
                   'geometry': {'type': 'Polygon', 'coordinates': [[[x, y] for x, y in ring]]}})
with open('plates.geojson', 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': pfeats}, f)

features = []
used = set()
dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
base = 1704067200000
while len(features) < 60:
    lon = round(random.uniform(-150, -70), 4)
    lat = round(random.uniform(-28, 38), 4)
    if min_edge(lon, lat) < 0.3:
        continue
    eid = 'zz%07d' % random.randint(0, 9999999)
    if eid in used:
        continue
    used.add(eid)
    mag = round(random.uniform(2.5, 7.2), 2)
    depth = round(random.uniform(1, 250), 2)
    t = base + random.randint(0, 365 * 86400 - 1) * 1000 + random.randint(0, 999)
    place = '%d km %s of Station %s' % (random.randint(3, 280), random.choice(dirs), chr(65 + random.randint(0, 25)))
    features.append({'type': 'Feature', 'id': eid,
                     'properties': {'id': eid, 'mag': mag, 'place': place, 'time': t, 'type': 'earthquake'},
                     'geometry': {'type': 'Point', 'coordinates': [lon, lat, depth]}})

with open('earthquakes.geojson', 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f)

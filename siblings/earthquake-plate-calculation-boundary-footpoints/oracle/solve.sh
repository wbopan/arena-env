#!/usr/bin/env bash
set -euo pipefail
cat > /root/work/solve.py <<'PY'
import csv
import json
import math
from pathlib import Path

base = Path('/root/work')
lines = json.loads((base/'boundaries.geojson').read_text())['features']
quakes = json.loads((base/'earthquakes.json').read_text())
km_per_degree = 6378137 * math.pi / 180 / 1000
with (base/'footpoints.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'boundary_id', 'foot_lon', 'foot_lat', 'distance_km', 'station_km'])
    for q in sorted(quakes, key=lambda item: item['id']):
        candidates = []
        for feature in lines:
            vertices = feature['geometry']['coordinates']
            offset = 0.0
            for a, b in zip(vertices, vertices[1:]):
                dx, dy = b[0]-a[0], b[1]-a[1]
                segment = math.hypot(dx, dy)
                t = max(0.0, min(1.0, ((q['longitude']-a[0])*dx+(q['latitude']-a[1])*dy)/(segment*segment)))
                lon, lat = a[0]+t*dx, a[1]+t*dy
                distance = math.hypot(q['longitude']-lon, q['latitude']-lat)*km_per_degree
                candidates.append((distance, feature['properties']['BoundaryID'], lon, lat, (offset+t*segment)*km_per_degree))
                offset += segment
        distance, name, lon, lat, station = min(candidates)
        writer.writerow([q['id'], name, f'{lon:.3f}', f'{lat:.3f}', f'{distance:.3f}', f'{station:.3f}'])
PY
python /root/work/solve.py

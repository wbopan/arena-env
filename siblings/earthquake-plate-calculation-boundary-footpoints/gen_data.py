import json
import random

random.seed(9271)
lines = [('B-N', [[0, 5], [3, 5], [6, 6]]), ('B-S', [[0, 0], [2, 1], [6, 1]]), ('B-E', [[8, -1], [8, 3], [9, 6]])]
features = [{'type': 'Feature', 'properties': {'BoundaryID': name}, 'geometry': {'type': 'LineString', 'coordinates': coords}} for name, coords in lines]
with open('boundaries.geojson', 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f)
quakes = []
for i in range(15):
    quakes.append({'id': f'q{i:02d}', 'longitude': round(random.uniform(-1, 10), 5), 'latitude': round(random.uniform(-1.5, 7), 5)})
with open('earthquakes.json', 'w') as f:
    json.dump(quakes, f)

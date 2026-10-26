import json
import random

random.seed(4107)
pa = [[0, 0], [7, 0], [8, 3], [6, 7], [1, 6], [0, 0]]
other = [[10, 0], [13, 0], [13, 3], [10, 3], [10, 0]]
features = []
for code, ring in [('PA', pa), ('XX', other)]:
    features.append({'type': 'Feature', 'properties': {'Code': code}, 'geometry': {'type': 'Polygon', 'coordinates': [ring]}})
with open('plates.geojson', 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f)
quakes = []
for i in range(32):
    lon = round(random.uniform(-0.5, 12.8), 5)
    lat = round(random.uniform(-0.5, 7.2), 5)
    quakes.append({'id': f'ev{i:02d}', 'longitude': lon, 'latitude': lat})
with open('earthquakes.json', 'w') as f:
    json.dump(quakes, f)

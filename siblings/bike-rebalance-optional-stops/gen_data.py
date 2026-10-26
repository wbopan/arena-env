import json
import random

random.seed(4107)
ids = [107, 26, 311, 58, 204, 91]
targets = [2, -2, 3, -1, 1, -3]
random.shuffle(targets)
stations = []
for sid, target in zip(ids, targets):
    stations.append({
        'id': sid,
        'latitude': round(40.72 + random.uniform(-0.038, 0.038), 6),
        'longitude': round(-73.98 + random.uniform(-0.038, 0.038), 6),
        'initial_bikes': 6,
        'station_capacity': 12,
        'net_rebalancing_target': target,
    })
data = {'depot': {'latitude': 40.72, 'longitude': -73.98},
        'vehicle_capacity': 5, 'start_load': 2, 'penalty_weight': 2.4,
        'stations': stations}
with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)

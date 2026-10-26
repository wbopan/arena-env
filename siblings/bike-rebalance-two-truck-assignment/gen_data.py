import json
import random

random.seed(8321)
ids = [402, 17, 136, 77, 291, 54]
targets = [3, -2, 2, -1, -1, -1]
random.shuffle(targets)
stations = []
for sid, target in zip(ids, targets):
    stations.append({'id': sid,
                     'latitude': round(40.73 + random.uniform(-0.04, 0.04), 6),
                     'longitude': round(-73.99 + random.uniform(-0.04, 0.04), 6),
                     'initial_bikes': 6, 'station_capacity': 12,
                     'net_rebalancing_target': target})
with open('data.json', 'w') as f:
    json.dump({'depot': {'latitude': 40.73, 'longitude': -73.99},
               'vehicle_capacity': 6,
               'vehicles': [{'vehicle_id': 8, 'start_load': 2},
                            {'vehicle_id': 3, 'start_load': 3}],
               'stations': stations}, f, indent=2)

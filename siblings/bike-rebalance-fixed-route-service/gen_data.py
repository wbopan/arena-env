import json
import random

random.seed(6229)
ids = [73, 208, 19, 145, 307, 52, 411]
stations = []
for sid in ids:
    stations.append({'id': sid,
                     'latitude': round(40.70 + random.uniform(-0.035, 0.035), 6),
                     'longitude': round(-73.96 + random.uniform(-0.035, 0.035), 6),
                     'initial_bikes': random.randint(3, 7),
                     'station_capacity': 10,
                     'net_rebalancing_target': random.randint(-3, 3),
                     'penalty_weight': random.choice([0.9, 1.3, 2.1, 3.2])})
with open('data.json', 'w') as f:
    json.dump({'depot': {'latitude': 40.70, 'longitude': -73.96},
               'route': ids, 'vehicle_capacity': 5, 'start_load': 2,
               'required_end_load': 2, 'handling_cost_per_bike': 0.18,
               'stations': stations}, f, indent=2)

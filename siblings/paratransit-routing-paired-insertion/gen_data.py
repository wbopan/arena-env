import csv
import json
import random

random.seed(55613)
ids = ['DEP', 'P0', 'D0', 'P1', 'D1', 'P2', 'D2']
locations = {n: (random.randrange(23), random.randrange(23)) for n in ids}
with open('t_matrix.csv', 'w', newline='') as f:
    csv.writer(f).writerows([[0 if a == b else abs(locations[a][0]-locations[b][0])+abs(locations[a][1]-locations[b][1])+2 for b in ids] for a in ids])
trips = []
for i in range(3):
    trips.append({'trip_id': str(i), 'pickup_node': f'P{i}', 'dropoff_node': f'D{i}', 'load': random.choice([1, 2]), 'pickup_tw': [480, 710], 'dropoff_tw': [480, 780], 'pickup_service_min': 4, 'dropoff_service_min': 3})
with open('requests.json', 'w') as f:
    json.dump(trips, f, indent=2)
with open('base_route.json', 'w') as f:
    json.dump({'start_min': 480, 'end_limit_min': 850, 'capacity': 3, 'node_sequence': ['DEP', 'P0', 'D0', 'P1', 'D1', 'DEP']}, f, indent=2)

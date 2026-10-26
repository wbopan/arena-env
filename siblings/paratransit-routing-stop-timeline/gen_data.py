import csv
import json
import random

random.seed(2417)
ids = ['DEP'] + [n for i in range(5) for n in (f'P{i}', f'D{i}')]
xy = {n: (random.randrange(18), random.randrange(18)) for n in ids}
matrix = [[0 if a == b else abs(xy[a][0]-xy[b][0])+abs(xy[a][1]-xy[b][1])+2 for b in ids] for a in ids]
with open('t_matrix.csv', 'w', newline='') as f:
    csv.writer(f).writerows(matrix)
sequence = ['DEP', 'P0', 'P1', 'D0', 'P2', 'D1', 'D2', 'P3', 'D3', 'P4', 'D4', 'DEP']
loads = [random.choice([1, 2]) for _ in range(5)]
requests = [{'trip_id': str(i), 'pickup_node': f'P{i}', 'dropoff_node': f'D{i}', 'load': loads[i], 'service_min': {'pickup': 3, 'dropoff': 2}, 'pickup_tw': None, 'dropoff_tw': None} for i in range(5)]
t = 480
for a, b in zip(sequence, sequence[1:]):
    t += matrix[ids.index(a)][ids.index(b)]
    if b != 'DEP':
        i = int(b[1:])
        kind = 'pickup' if b[0] == 'P' else 'dropoff'
        low = t + random.randrange(5)
        requests[i][kind + '_tw'] = [low, low + 15]
        t = low + requests[i]['service_min'][kind]
with open('requests.json', 'w') as f:
    json.dump(requests, f, indent=2)
with open('route.json', 'w') as f:
    json.dump({'start_min': 480, 'node_sequence': sequence}, f, indent=2)

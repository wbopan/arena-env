import csv
import json
import random

random.seed(89104)
groups = []
for i in range(5):
    groups.append({'group_id': f'G{i}', 'trips': [{'trip_id': f'{i}-{j}', 'pickup_node': f'P{i}_{j}', 'dropoff_node': f'D{i}_{j}'} for j in range(2)]})
ids = ['DEP'] + [n for group in groups for trip in group['trips'] for n in (trip['pickup_node'], trip['dropoff_node'])]
points = {n: (random.randrange(25), random.randrange(25)) for n in ids}
with open('t_matrix.csv', 'w', newline='') as f:
    csv.writer(f).writerows([[0 if a == b else abs(points[a][0]-points[b][0])+abs(points[a][1]-points[b][1])+1 for b in ids] for a in ids])
order = list(range(5))
random.shuffle(order)
incomplete = set(random.sample(order, 2))
routes = [['DEP'], ['DEP']]
for i in order:
    routes[0].extend([f'P{i}_0', f'D{i}_0'])
    routes[1].append(f'P{i}_1')
    if i not in incomplete:
        routes[1].append(f'D{i}_1')
for route in routes:
    route.append('DEP')
with open('requests.json', 'w') as f:
    json.dump(groups, f, indent=2)
with open('candidate_routes.json', 'w') as f:
    json.dump({'routes': routes}, f, indent=2)

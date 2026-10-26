#!/bin/bash
set -e
cat > /tmp/connected_cleanup_solution.py <<'PY'
import csv
import json
from pathlib import Path

root = Path('/root/work')
groups = json.loads((root / 'requests.json').read_text())
routes = json.loads((root / 'candidate_routes.json').read_text())['routes']
with (root / 't_matrix.csv').open() as f:
    matrix = [list(map(int, row)) for row in csv.reader(f)]
nodes = ['DEP'] + [node for group in groups for trip in group['trips'] for node in (trip['pickup_node'], trip['dropoff_node'])]
completed = []
retained = set()
for group in groups:
    positions = {}
    for vehicle, route in enumerate(routes):
        for index, node in enumerate(route):
            positions.setdefault(node, []).append((vehicle, index))
    good = True
    for trip in group['trips']:
        p, d = positions.get(trip['pickup_node'], []), positions.get(trip['dropoff_node'], [])
        if len(p) != 1 or len(d) != 1 or p[0][0] != d[0][0] or p[0][1] >= d[0][1]:
            good = False
    if good:
        completed.append(group['group_id'])
        for trip in group['trips']:
            retained.add(trip['pickup_node'])
            retained.add(trip['dropoff_node'])
cleaned = [[node for node in route if node == 'DEP' or node in retained] for route in routes]
minutes = sum(matrix[nodes.index(a)][nodes.index(b)] for route in cleaned for a, b in zip(route, route[1:]))
(root / 'cleaned_plan.json').write_text(json.dumps({'complete_group_ids': sorted(completed), 'cleaned_routes': cleaned, 'total_travel_min': minutes}, indent=2) + '\n')
PY
python3 /tmp/connected_cleanup_solution.py

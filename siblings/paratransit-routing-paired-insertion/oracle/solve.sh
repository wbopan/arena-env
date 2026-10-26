#!/bin/bash
set -e
cat > /tmp/paired_insertion_solution.py <<'PY'
import csv
import json
from pathlib import Path

root = Path('/root/work')
trips = json.loads((root / 'requests.json').read_text())
base = json.loads((root / 'base_route.json').read_text())
with (root / 't_matrix.csv').open() as f:
    matrix = [list(map(int, row)) for row in csv.reader(f)]
nodes = ['DEP'] + [node for trip in trips for node in (trip['pickup_node'], trip['dropoff_node'])]
lookup = {node: i for i, node in enumerate(nodes)}
def travel(route):
    return sum(matrix[lookup[a]][lookup[b]] for a, b in zip(route, route[1:]))
def schedule(route):
    time, load, times = base['start_min'], 0, []
    for a, b in zip(route, route[1:]):
        time += matrix[lookup[a]][lookup[b]]
        if b == 'DEP':
            return times if time <= base['end_limit_min'] and load == 0 else None
        trip = next(t for t in trips if b == t['pickup_node'] or b == t['dropoff_node'])
        kind = 'pickup' if b == trip['pickup_node'] else 'dropoff'
        time = max(time, trip[kind + '_tw'][0])
        if time > trip[kind + '_tw'][1]:
            return None
        times.append(time)
        load += trip['load'] if kind == 'pickup' else -trip['load']
        if load < 0 or load > base['capacity']:
            return None
        time += trip[kind + '_service_min']
    return None
baseline = travel(base['node_sequence'])
options = []
for pickup_index in range(6):
    for dropoff_index in range(pickup_index + 1, 6):
        stops = base['node_sequence'][1:-1].copy()
        stops.insert(pickup_index, trips[2]['pickup_node'])
        stops.insert(dropoff_index, trips[2]['dropoff_node'])
        route = ['DEP'] + stops + ['DEP']
        times = schedule(route)
        if times is not None:
            options.append((travel(route) - baseline, pickup_index, dropoff_index, times))
cost, pickup, dropoff, starts = min(options, key=lambda item: item[:3])
(root / 'insertion.json').write_text(json.dumps({'pickup_index': pickup, 'dropoff_index': dropoff, 'added_travel_min': cost, 'service_starts_min': starts}, indent=2) + '\n')
PY
python3 /tmp/paired_insertion_solution.py

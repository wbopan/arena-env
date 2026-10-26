#!/bin/bash
set -e
cat > /tmp/stop_timeline_solution.py <<'PY'
import csv
import json
from pathlib import Path

root = Path('/root/work')
requests = json.loads((root / 'requests.json').read_text())
route = json.loads((root / 'route.json').read_text())
with (root / 't_matrix.csv').open() as f:
    travel = [list(map(int, row)) for row in csv.reader(f)]
nodes = ['DEP'] + [node for trip in requests for node in (trip['pickup_node'], trip['dropoff_node'])]
time = route['start_min']
load = 0
rows = [['DEP', time, time, time, 0, 0]]
for old, node in zip(route['node_sequence'][:-1], route['node_sequence'][1:]):
    arrival = time + travel[nodes.index(old)][nodes.index(node)]
    start, service = arrival, 0
    if node != 'DEP':
        trip = next(trip for trip in requests if node in (trip['pickup_node'], trip['dropoff_node']))
        pickup = node == trip['pickup_node']
        kind = 'pickup' if pickup else 'dropoff'
        start = max(arrival, trip[kind + '_tw'][0])
        service = trip['service_min'][kind]
        load += trip['load'] if pickup else -trip['load']
    time = start + service
    rows.append([node, arrival, start, time, start-arrival, load])
with (root / 'timeline.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['node', 'arrival_min', 'start_min', 'depart_min', 'wait_min', 'load_after'])
    writer.writerows(rows)
PY
python3 /tmp/stop_timeline_solution.py

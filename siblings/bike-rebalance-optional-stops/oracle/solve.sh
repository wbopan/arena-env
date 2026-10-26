#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/bike_optional_solve.py <<'PY'
import itertools
import json
import math

with open('data.json') as f:
    d = json.load(f)
by_id = {s['id']: s for s in d['stations']}
ids = sorted(by_id)

def miles(a, b):
    x, y = math.radians(a['latitude']), math.radians(b['latitude'])
    delta = math.radians(b['longitude'] - a['longitude'])
    c = math.sin(x)*math.sin(y) + math.cos(x)*math.cos(y)*math.cos(delta)
    return 3960.0 * math.acos(max(-1.0, min(1.0, c)))

best = None
for size in range(len(ids) + 1):
    for path in itertools.permutations(ids, size):
        load = d['start_load']
        if any(not (0 <= (load := load + by_id[i]['net_rebalancing_target']) <= d['vehicle_capacity']) or not (0 <= by_id[i]['initial_bikes'] - by_id[i]['net_rebalancing_target'] <= by_id[i]['station_capacity']) for i in path):
            continue
        nodes = [d['depot']] + [by_id[i] for i in path] + [d['depot']]
        travel = sum(miles(a, b) for a, b in zip(nodes, nodes[1:])) if path else 0.0
        penalty = d['penalty_weight'] * sum(abs(by_id[i]['net_rebalancing_target']) for i in ids if i not in path)
        cost = travel + penalty
        if best is None or cost < best[0] - 1e-9 or (abs(cost - best[0]) <= 1e-9 and path < best[1]):
            best = cost, path, travel, penalty
cost, path, travel, penalty = best
with open('route.json', 'w') as f:
    json.dump({'route': ['depot_start', *path, 'depot_end'], 'travel_distance_miles': round(travel, 6), 'unmet_penalty': round(penalty, 6), 'objective': round(cost, 6)}, f, indent=2)
PY
python /tmp/bike_optional_solve.py

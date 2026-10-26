#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/bike_assignment_solve.py <<'PY'
import itertools
import json
import math

with open('data.json') as f:
    d = json.load(f)
s = {x['id']: x for x in d['stations']}

def dist(a, b):
    p = math.radians(a['latitude'])
    q = math.radians(b['latitude'])
    z = math.sin(p)*math.sin(q) + math.cos(p)*math.cos(q)*math.cos(math.radians(a['longitude']-b['longitude']))
    return 3960 * math.acos(max(-1, min(1, z)))

def trace(path, v):
    load = v['start_load']
    loads = []
    for i in path:
        load += s[i]['net_rebalancing_target']
        if not 0 <= load <= d['vehicle_capacity'] or not 0 <= s[i]['initial_bikes']-s[i]['net_rebalancing_target'] <= s[i]['station_capacity']:
            return None
        loads.append(load)
    return loads

def length(path):
    nodes = [d['depot'], *(s[i] for i in path), d['depot']]
    return sum(dist(a, b) for a, b in zip(nodes, nodes[1:]))

best = None
for perm in itertools.permutations(sorted(s)):
    for cut in range(1, len(perm)):
        paths = (perm[:cut], perm[cut:])
        if any(trace(paths[j], d['vehicles'][j]) is None for j in (0, 1)):
            continue
        cost = length(paths[0]) + length(paths[1])
        if best is None or cost < best[0]-1e-9 or (abs(cost-best[0]) <= 1e-9 and paths < best[1]):
            best = (cost, paths)
cost, paths = best
vehicles = []
for v, path in zip(d['vehicles'], paths):
    loads = trace(path, v)
    vehicles.append({'vehicle_id': v['vehicle_id'], 'route': ['depot_start', *path, 'depot_end'], 'loads_after_stops': loads, 'end_load': loads[-1]})
with open('assignment.json', 'w') as f:
    json.dump({'vehicles': vehicles, 'travel_distance_miles': round(cost, 6)}, f, indent=2)
PY
python /tmp/bike_assignment_solve.py

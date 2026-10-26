#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/bike_service_solve.py <<'PY'
import json
import math

with open('data.json') as f:
    d = json.load(f)
stations = {s['id']: s for s in d['stations']}

def miles(a, b):
    p, q = math.radians(a['latitude']), math.radians(b['latitude'])
    c = math.sin(p)*math.sin(q) + math.cos(p)*math.cos(q)*math.cos(math.radians(a['longitude']-b['longitude']))
    return 3960 * math.acos(max(-1, min(1, c)))

nodes = [d['depot'], *(stations[i] for i in d['route']), d['depot']]
travel = sum(miles(a, b) for a, b in zip(nodes, nodes[1:]))
# Each state records the cheapest service prefix ending at that truck load.
dp = {d['start_load']: (0.0, ())}
for sid in d['route']:
    s = stations[sid]
    following = {}
    for old_load, (old_cost, path) in dp.items():
        for new_load in range(d['vehicle_capacity']+1):
            service = new_load-old_load
            if not 0 <= s['initial_bikes']-service <= s['station_capacity']:
                continue
            cost = old_cost + s['penalty_weight']*abs(s['net_rebalancing_target']-service) + d['handling_cost_per_bike']*abs(service)
            candidate = (cost, path+(service,))
            previous = following.get(new_load)
            if previous is None or cost < previous[0]-1e-9 or (abs(cost-previous[0]) <= 1e-9 and candidate[1] < previous[1]):
                following[new_load] = candidate
    dp = following
_, services = dp[d['required_end_load']]
load = d['start_load']
loads = []
for q in services:
    load += q
    loads.append(load)
penalty = sum(stations[i]['penalty_weight']*abs(stations[i]['net_rebalancing_target']-q) for i, q in zip(d['route'], services))
handling = d['handling_cost_per_bike']*sum(map(abs, services))
with open('service.json', 'w') as f:
    json.dump({'route': ['depot_start', *d['route'], 'depot_end'], 'net_pickups': services, 'loads_after_stops': loads, 'travel_distance_miles': round(travel, 6), 'unmet_penalty': round(penalty, 6), 'handling_cost': round(handling, 6), 'objective': round(travel+penalty+handling, 6)}, f, indent=2)
PY
python /tmp/bike_service_solve.py

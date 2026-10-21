#!/bin/bash
set -e
cd /root/work
cat > /tmp/audit_plan.py <<'EOF'
import json
import math

data = json.load(open('data.json'))
plan = json.load(open('plan.json'))
cap = data['vehicle_capacity']
st = {s['id']: s for s in data['stations']}


def dist(a, b):
    phi1 = math.radians(90.0 - a['latitude'])
    phi2 = math.radians(90.0 - b['latitude'])
    dt = math.radians(a['longitude'] - b['longitude'])
    c = math.sin(phi1) * math.sin(phi2) * math.cos(dt) + math.cos(phi1) * math.cos(phi2)
    return math.acos(max(-1.0, min(1.0, c))) * 3960.0


pick = {k: 0 for k in st}
drop = {k: 0 for k in st}
vehicles = []
ok_all = True
travel = 0.0
for v in plan['vehicles']:
    nodes = [data['depot']] + [st[s['station_id']] for s in v['stops']] + [data['depot']]
    d = sum(dist(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1))
    travel += d
    load = v['start_load']
    loads = [load]
    for s in v['stops']:
        load += s['bikes_picked_up'] - s['bikes_dropped_off']
        loads.append(load)
        pick[s['station_id']] += s['bikes_picked_up']
        drop[s['station_id']] += s['bikes_dropped_off']
    ok = min(loads) >= 0 and max(loads) <= cap
    ok_all = ok_all and ok
    vehicles.append({'vehicle_id': v['vehicle_id'], 'distance_miles': round(d, 4), 'min_load': min(loads),
                     'max_load': max(loads), 'end_load': loads[-1], 'capacity_ok': bool(ok)})
stations = []
unmet_total = 0
for s in data['stations']:
    k = s['id']
    fin = s['initial_bikes'] - pick[k] + drop[k]
    ok = 0 <= fin <= s['station_capacity']
    ok_all = ok_all and ok
    unmet = abs(s['net_rebalancing_target'] - (pick[k] - drop[k]))
    unmet_total += unmet
    stations.append({'station_id': k, 'total_bikes_picked_up': pick[k], 'total_bikes_dropped_off': drop[k],
                     'final_inventory': fin, 'inventory_ok': bool(ok), 'unmet_rebalancing_amount': unmet})
pen = data['penalty_weight'] * unmet_total
summary = {'travel_distance_miles': round(travel, 4), 'total_unmet_rebalancing_amount': unmet_total,
           'unmet_rebalancing_penalty': round(pen, 4), 'objective': round(travel + pen, 4),
           'all_feasible': bool(ok_all)}
json.dump({'vehicles': vehicles, 'stations': stations, 'summary': summary}, open('audit.json', 'w'), indent=2)
EOF
python3 /tmp/audit_plan.py

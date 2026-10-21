#!/bin/bash
set -e
cd /root/work
cat > /tmp/sequence.py <<'EOF'
import csv
import itertools
import json
import math

data = json.load(open('truck.json'))
S = data['stations']
n = len(S)
cap = data['vehicle_capacity']
start = data['start_load']
pts = S + [data['depot']]


def dist(a, b):
    phi1 = math.radians(90.0 - a['latitude'])
    phi2 = math.radians(90.0 - b['latitude'])
    dt = math.radians(a['longitude'] - b['longitude'])
    c = math.sin(phi1) * math.sin(phi2) * math.cos(dt) + math.cos(phi1) * math.cos(phi2)
    return math.acos(max(-1.0, min(1.0, c))) * 3960.0


D = [[dist(a, b) for b in pts] for a in pts]
t = [s['net_rebalancing_target'] for s in S]
best = None
best_perm = None
for perm in itertools.permutations(range(n)):
    load = start
    ok = True
    for i in perm:
        load += t[i]
        if load < 0 or load > cap:
            ok = False
            break
    if not ok:
        continue
    d = D[n][perm[0]] + D[perm[-1]][n] + sum(D[perm[k]][perm[k + 1]] for k in range(n - 1))
    if best is None or d < best:
        best, best_perm = d, perm
with open('route.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['position', 'station_id', 'bikes_picked_up', 'bikes_dropped_off', 'load_after_stop'])
    load = start
    for pos, i in enumerate(best_perm, 1):
        load += t[i]
        w.writerow([pos, S[i]['id'], max(t[i], 0), max(-t[i], 0), load])
EOF
python3 /tmp/sequence.py

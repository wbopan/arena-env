#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json
reqs = json.load(open('requests.json'))
cfg = json.load(open('config.json'))
plan = json.load(open('plan.json'))
M = [list(map(int, l.split(','))) for l in open('t_matrix.csv') if l.strip()]
D = cfg['depot_node']
node = {}
for rq in reqs:
    for tr in rq['trips']:
        node[tr['pickup_node']] = (tr, 'p')
        node[tr['dropoff_node']] = (tr, 'd')
out = []
served = set()
for r in plan['routes']:
    seq = r['node_sequence']
    idx = {n: i for i, n in enumerate(seq)}
    feas = True
    t = r['start_time']; prev = D; load = 0; mx = 0; wait = 0; start = {}
    for n in seq:
        tr, kind = node[n]
        a = t + M[prev][n]
        lo, hi = tr['pickup_tw'] if kind == 'p' else tr['dropoff_tw']
        s = max(a, lo); wait += s - a
        if s > hi: feas = False
        start[n] = s
        load += tr['load'] if kind == 'p' else -tr['load']
        mx = max(mx, load)
        if load > cfg['capacity']: feas = False
        t = s + cfg['service_time']; prev = n
    end = t + M[prev][D]
    if end - r['start_time'] > cfg['shift_duration']: feas = False
    for n in seq:
        tr, kind = node[n]
        p, d = tr['pickup_node'], tr['dropoff_node']
        if p not in idx or d not in idx or idx[p] > idx[d]:
            feas = False
        elif start[d] - start[p] > cfg['max_ride_time']:
            feas = False
    if feas:
        for n in seq: served.add(node[n][0]['trip_id'])
    out.append({'vehicle_id': r['vehicle_id'], 'feasible': feas, 'end_time': end, 'max_load': mx, 'total_wait': wait})
sr = []; st = []
for rq in reqs:
    ids = [x['trip_id'] for x in rq['trips']]
    if all(i in served for i in ids):
        sr.append(rq['request_id']); st += ids
json.dump({'routes': out, 'served_trips': sorted(st), 'served_requests': sorted(sr)}, open('report.json', 'w'), indent=1)
EOF
python3 /tmp/solve.py

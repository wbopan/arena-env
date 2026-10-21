#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_cost.py <<'EOF'
import json

case = json.load(open('case.json'))
sch = json.load(open('schedule.json'))['generators']
T = case['time_periods']

def curve_cost(points, x):
    pts = sorted((float(q['mw']), float(q['cost'])) for q in points)
    if x <= pts[0][0]:
        return pts[0][1]
    for (a, ca), (b, cb) in zip(pts, pts[1:]):
        if x <= b:
            return ca + (cb - ca) * (x - a) / (b - a)
    return pts[-1][1]

out = []
for name, g in case['thermal_generators'].items():
    u = sch[name]['commitment']
    p = sch[name]['production_MW']
    tiers = sorted(g['startup'], key=lambda z: z['lag'])
    status = g['unit_on_t0']
    off = g['time_down_t0'] if status == 0 else 0
    pc = sc = 0.0
    ns = 0
    for t in range(T):
        if u[t]:
            pc += curve_cost(g['piecewise_production'], p[t])
            if not status:
                ns += 1
                ok = [z for z in tiers if z['lag'] <= off]
                sc += (ok[-1] if ok else tiers[0])['cost']
            off = 0
        else:
            off += 1
        status = u[t]
    out.append({'name': name, 'num_startups': ns, 'production_cost': round(pc, 2),
                'startup_cost': round(sc, 2), 'total_cost': round(pc + sc, 2)})

tp = sum(o['production_cost'] for o in out)
ts = sum(o['startup_cost'] for o in out)
rep = {'generators': out, 'total_production_cost': round(tp, 2),
       'total_startup_cost': round(ts, 2), 'total_cost': round(tp + ts, 2)}
json.dump(rep, open('cost_report.json', 'w'), indent=2)
EOF
python3 /tmp/solve_cost.py

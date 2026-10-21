#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_ed.py <<'EOF'
import json

d = json.load(open('/root/work/network.json'))
gens, gc = d['gen'], d['gencost']
load = sum(b[2] for b in d['bus'])
on = [i for i, g in enumerate(gens) if int(g[7]) == 1]

def pout(i, lam):
    p = (lam - gc[i][5]) / (2 * gc[i][4])
    return min(max(p, gens[i][9]), gens[i][8])

lo, hi = 0.0, 2000.0
for _ in range(300):
    lam = (lo + hi) / 2
    if sum(pout(i, lam) for i in on) < load:
        lo = lam
    else:
        hi = lam
lam = (lo + hi) / 2
P = [pout(i, lam) if i in on else 0.0 for i in range(len(gens))]
cost = sum(gc[i][4] * P[i] ** 2 + gc[i][5] * P[i] + gc[i][6] for i in on)
margin = sum(gens[i][8] - P[i] for i in on)
rep = {
    'generators': [{'id': i + 1, 'bus': int(g[0]), 'output_MW': round(P[i], 2)} for i, g in enumerate(gens)],
    'system_lambda': round(lam, 3),
    'total_cost': round(cost, 2),
    'load_MW': round(load, 2),
    'spinning_margin_MW': round(margin, 2),
}
json.dump(rep, open('/root/work/dispatch.json', 'w'), indent=2)
EOF
python3 /tmp/solve_ed.py

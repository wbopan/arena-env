#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_pf.py <<'EOF'
import json
import numpy as np

d = json.load(open('/root/work/network.json'))
base = float(d['baseMVA'])
bus = d['bus']
idx = {int(b[0]): i for i, b in enumerate(bus)}
n = len(bus)
p = np.array([-float(b[2]) for b in bus])
for g in d['gen']:
    if int(g[7]) == 1:
        p[idx[int(g[0])]] += float(g[1])
p /= base
live = [br for br in d['branch'] if int(br[10]) == 1]
B = np.zeros((n, n))
for br in live:
    f, t = idx[int(br[0])], idx[int(br[1])]
    b = 1.0 / br[3]
    B[f, f] += b; B[t, t] += b; B[f, t] -= b; B[t, f] -= b
s = [i for i, b in enumerate(bus) if int(b[1]) == 3][0]
k = [i for i in range(n) if i != s]
th = np.zeros(n)
th[k] = np.linalg.solve(B[np.ix_(k, k)], p[k])
with open('/root/work/branch_flows.csv', 'w') as fh:
    fh.write('from_bus,to_bus,flow_MW,loading_pct\n')
    for br in live:
        f, t = idx[int(br[0])], idx[int(br[1])]
        fl = (th[f] - th[t]) / br[3] * base
        fh.write('%d,%d,%.2f,%.2f\n' % (int(br[0]), int(br[1]), fl, abs(fl) / br[5] * 100))
EOF
python3 /tmp/solve_pf.py

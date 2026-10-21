#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import json, math, csv
import numpy as np
net = json.load(open('/root/work/network.json'))
base = float(net['baseMVA'])
idx = {int(b[0]): i for i, b in enumerate(net['bus'])}
Vm = np.array([b[7] for b in net['bus']], float)
Va = np.deg2rad([b[8] for b in net['bus']])
out = []
for br in net['branch']:
    if int(br[10]) != 1:
        continue
    r, x, bc = br[2], br[3], br[4]
    tap = br[8] if abs(br[8]) > 1e-12 else 1.0
    sh = math.radians(br[9])
    d = r*r + x*x
    g, b = r/d, -x/d
    i, j = idx[int(br[0])], idx[int(br[1])]
    vi, vj = Vm[i], Vm[j]
    it = 1.0/tap
    dij = Va[i] - Va[j] - sh
    dji = -dij
    Pij = g*vi*vi*it*it - vi*vj*it*(g*math.cos(dij) + b*math.sin(dij))
    Qij = -(b + bc/2)*vi*vi*it*it - vi*vj*it*(g*math.sin(dij) - b*math.cos(dij))
    Pji = g*vj*vj - vi*vj*it*(g*math.cos(dji) + b*math.sin(dji))
    Qji = -(b + bc/2)*vj*vj - vi*vj*it*(g*math.sin(dji) - b*math.cos(dji))
    Pij, Qij, Pji, Qji = [v*base for v in (Pij, Qij, Pji, Qji)]
    rate = br[5]
    load = 100*max(math.hypot(Pij, Qij), math.hypot(Pji, Qji))/rate if rate > 0 else 0.0
    out.append([int(br[0]), int(br[1])] + [round(v, 4) for v in (Pij, Qij, Pji, Qji, Pij + Pji, load)])
with open('/root/work/branch_flows.csv', 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['from_bus','to_bus','p_from_MW','q_from_MVAr','p_to_MW','q_to_MVAr','loss_MW','loading_pct'])
    w.writerows(out)
EOF
python3 /tmp/solve.py

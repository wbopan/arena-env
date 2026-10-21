#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv
import json
import numpy as np

d = json.load(open("network.json"))
base = d["baseMVA"]
bus = d["bus"]
idx = {int(b[0]): i for i, b in enumerate(bus)}
n = len(bus)
P = np.zeros(n)
for b in bus:
    P[idx[int(b[0])]] -= b[2]
for g in d["gen"]:
    if g[7] == 1:
        P[idx[int(g[0])]] += g[1]
P /= base
br = [b for b in d["branch"] if b[10] == 1]
B = np.zeros((n, n))
for b in br:
    f, t = idx[int(b[0])], idx[int(b[1])]
    y = 1.0 / b[3]
    B[f, f] += y
    B[t, t] += y
    B[f, t] -= y
    B[t, f] -= y
s = next(i for i, b in enumerate(bus) if b[1] == 3)
keep = [i for i in range(n) if i != s]
th = np.zeros(n)
th[keep] = np.linalg.solve(B[np.ix_(keep, keep)], P[keep])
with open("branch_flows.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["from_bus", "to_bus", "flow_MW", "loading_pct"])
    for b in br:
        f, t = idx[int(b[0])], idx[int(b[1])]
        fl = (th[f] - th[t]) / b[3] * base
        w.writerow([int(b[0]), int(b[1]), round(float(fl), 2), round(abs(float(fl)) / b[5] * 100, 2)])
EOF
python3 /tmp/solve.py

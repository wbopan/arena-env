#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json

d = json.load(open("network.json"))
load = sum(b[2] for b in d["bus"])
on = [k for k, g in enumerate(d["gen"]) if g[7] == 1]


def out(k, lam):
    g = d["gen"][k]
    c = d["gencost"][k]
    return min(max((lam - c[5]) / (2 * c[4]), g[9]), g[8])


lo, hi = 0.0, 1000.0
for _ in range(200):
    m = (lo + hi) / 2
    if sum(out(k, m) for k in on) < load:
        lo = m
    else:
        hi = m
lam = (lo + hi) / 2
gens = []
cost = 0.0
for k in on:
    g = d["gen"][k]
    c = d["gencost"][k]
    p = out(k, lam)
    cost += c[4] * p * p + c[5] * p + c[6]
    if abs(p - g[8]) <= 0.01:
        lim = "pmax"
    elif abs(p - g[9]) <= 0.01:
        lim = "pmin"
    else:
        lim = "none"
    gens.append({"gen_index": k + 1, "bus": int(g[0]), "output_MW": round(p, 3), "at_limit": lim})
rep = {"total_load_MW": round(load, 3),
       "system_lambda_dollars_per_MWh": round(lam, 4),
       "total_cost_dollars_per_hour": round(cost, 4),
       "generators": gens}
with open("dispatch.json", "w") as f:
    json.dump(rep, f, indent=2)
EOF
python3 /tmp/solve.py

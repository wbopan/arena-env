import json
import random

random.seed(7)
n_bus = 12
ids = sorted(random.sample(range(1, 400), n_bus))
buses = []
for i, bid in enumerate(ids):
    btype = 3 if i == 0 else random.choice([1, 1, 2])
    vm = round(random.uniform(0.94, 1.06), 4)
    va = 0.0 if i == 0 else round(random.uniform(-20.0, 8.0), 3)
    pd = round(random.uniform(0, 120), 2)
    qd = round(random.uniform(0, 40), 2)
    buses.append([bid, btype, pd, qd, 0.0, 0.0, 1, vm, va, 230.0, 1, 1.1, 0.9])

branches = []
for k in range(18):
    if k < n_bus - 1:
        f, t = ids[k], ids[k + 1]
    else:
        f, t = random.sample(ids, 2)
    r = round(random.uniform(0.002, 0.04), 5)
    x = round(random.uniform(0.02, 0.25), 5)
    b = round(random.uniform(0.0, 0.12), 4)
    tap, shift = 0.0, 0.0
    if k in (2, 6, 13, 16):
        tap = round(random.uniform(0.95, 1.06), 4)
        if k in (6, 16):
            shift = round(random.uniform(-8.0, 8.0), 2)
    rate = random.choice([0, 80, 120, 150, 200, 250, 300])
    status = 0 if k in (5, 14) else 1
    branches.append([f, t, r, x, b, rate, rate, rate, tap, shift, status, -360, 360])

with open("network.json", "w") as fh:
    json.dump({"baseMVA": 100.0, "bus": buses, "branch": branches}, fh, indent=1)

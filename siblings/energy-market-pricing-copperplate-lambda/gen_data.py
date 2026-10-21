import json
import random

random.seed(4242)
NB = 8
nums = sorted(random.sample(range(10, 900), NB))
slack = random.choice(nums)
NG = 9
gens = []
gencost = []
for k in range(NG):
    gb = random.choice(nums)
    pmax = float(random.randint(80, 300))
    pmin = float(round(pmax * random.uniform(0.1, 0.3)))
    status = 0 if k in (2, 6) else 1
    gens.append([gb, 0.0, 0.0, 100, -100, 1.0, 100, status, pmax, pmin])
    gencost.append([2, 0, 0, 3, round(random.uniform(0.002, 0.05), 4),
                    round(random.uniform(10, 45), 2), float(random.randint(50, 400))])

on = [k for k in range(NG) if gens[k][7] == 1]


def out(lam):
    res = []
    for k in on:
        c2, c1 = gencost[k][4], gencost[k][5]
        res.append(min(max((lam - c1) / (2 * c2), gens[k][9]), gens[k][8]))
    return res


def ok(load):
    lo, hi = 0.0, 1000.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if sum(out(mid)) < load:
            lo = mid
        else:
            hi = mid
    p = out(0.5 * (lo + hi))
    interior = 0
    for k, pk in zip(on, p):
        dl = min(pk - gens[k][9], gens[k][8] - pk)
        if 1e-9 < dl < 0.5:
            return False
        if dl >= 0.5:
            interior += 1
    return interior >= 2


pmin_sum = sum(gens[k][9] for k in on)
pmax_sum = sum(gens[k][8] for k in on)
frac = 0.45
while True:
    target = pmin_sum + frac * (pmax_sum - pmin_sum)
    w = [random.uniform(0.5, 1.5) for _ in nums]
    pds = [round(target * x / sum(w), 1) for x in w]
    if ok(sum(pds)):
        break
    frac += 0.013
    if frac > 0.8:
        frac = 0.3

buses = []
for n, pd in zip(nums, pds):
    t = 3 if n == slack else 1
    buses.append([n, t, pd, round(pd * 0.25, 1), 0, 0, 1, 1.0, 0, 230, 1, 1.05, 0.95])

data = {"baseMVA": 100.0, "bus": buses, "gen": gens, "gencost": gencost}
with open("network.json", "w") as f:
    json.dump(data, f, indent=1)

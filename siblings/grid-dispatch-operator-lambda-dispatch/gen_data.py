import json
import random

random.seed(4242)
BUS_NUMS = [1, 3, 4, 6, 8, 11]


def clip_out(c2, c1, pmin, pmax, lam):
    return min(max((lam - c1) / (2 * c2), pmin), pmax)


def count_interior(gens, costs, load):
    on = [i for i, g in enumerate(gens) if g[7] == 1]
    lo, hi = 0.0, 1000.0
    for _ in range(200):
        lam = 0.5 * (lo + hi)
        tot = sum(clip_out(costs[i][4], costs[i][5], gens[i][9], gens[i][8], lam) for i in on)
        if tot < load:
            lo = lam
        else:
            hi = lam
    cnt = 0
    for i in on:
        p = clip_out(costs[i][4], costs[i][5], gens[i][9], gens[i][8], lam)
        if gens[i][9] + 1 < p < gens[i][8] - 1:
            cnt += 1
    return cnt


while True:
    gens = []
    costs = []
    for k in range(8):
        bus = random.choice(BUS_NUMS)
        pmin = round(random.uniform(10, 40), 1)
        pmax = round(pmin + random.uniform(80, 250), 1)
        status = 0 if k == 5 else 1
        prev = round(random.uniform(pmin, pmax), 1)
        gens.append([bus, prev, 0.0, 80.0, -60.0, 1.0, 100.0, status, pmax, pmin])
        c2 = round(random.uniform(0.004, 0.04), 5)
        c1 = 8.0 if k == 5 else round(random.uniform(14, 45), 2)
        c0 = round(random.uniform(50, 400), 1)
        costs.append([2, 0.0, 0.0, 3, c2, c1, c0])
    cap = sum(g[8] for g in gens if g[7] == 1)
    target = random.uniform(0.45, 0.65) * cap
    w = [random.random() + 0.2 for _ in BUS_NUMS]
    buses = []
    for j, b in enumerate(BUS_NUMS):
        pd = round(target * w[j] / sum(w), 1)
        buses.append([b, 3 if j == 0 else 1, pd, round(0.25 * pd, 1), 0.0, 0.0, 1, 1.0, 0.0, 138.0, 1, 1.06, 0.94])
    load = sum(b[2] for b in buses)
    if count_interior(gens, costs, load) >= 2:
        break

with open('network.json', 'w') as fh:
    json.dump({'baseMVA': 100.0, 'bus': buses, 'gen': gens, 'gencost': costs}, fh, indent=1)

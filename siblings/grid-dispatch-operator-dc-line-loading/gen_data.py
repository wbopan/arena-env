import json
import random

random.seed(20240611)
base = 100.0
bus_nums = [1, 2, 4, 5, 7, 9, 10, 12, 15, 18, 21, 24]
slack = 4
# (bus, Pg or None for random, status)
gen_spec = [(4, 0.0, 1), (9, None, 1), (15, None, 1), (21, None, 1), (2, None, 0), (12, None, 1)]
gen_buses = {g[0] for g in gen_spec if g[2] == 1}

buses = []
for b in bus_nums:
    typ = 3 if b == slack else (2 if b in gen_buses else 1)
    pd = round(random.uniform(12.0, 60.0), 1)
    buses.append([b, typ, pd, round(0.3 * pd, 1), 0.0, 0.0, 1, 1.0, 0.0, 230.0, 1, 1.1, 0.9])

gens = []
for bus, pg, st in gen_spec:
    if pg is None:
        pg = round(random.uniform(30.0, 80.0), 1)
        pmax = round(max(pg * 1.5, 100.0), 1)
    else:
        pmax = 400.0
    gens.append([bus, pg, 0.0, 100.0, -100.0, 1.0, base, st, pmax, 0.0])

n = len(bus_nums)
pairs = [(bus_nums[i], bus_nums[(i + 1) % n]) for i in range(n)]
chords = [(1, 7), (2, 10), (5, 15), (9, 21), (12, 24), (4, 18)]
branches = []
for f, t in pairs + chords:
    x = round(random.uniform(0.04, 0.25), 4)
    rate = float(random.choice([80, 100, 120, 150, 180, 200, 250]))
    status = 0 if (f, t) == (2, 10) else 1
    branches.append([f, t, round(0.1 * x, 4), x, round(random.uniform(0.0, 0.05), 4),
                     rate, rate, rate, 0.0, 0.0, status, -360.0, 360.0])

with open('network.json', 'w') as fh:
    json.dump({'baseMVA': base, 'bus': buses, 'gen': gens, 'branch': branches}, fh, indent=1)

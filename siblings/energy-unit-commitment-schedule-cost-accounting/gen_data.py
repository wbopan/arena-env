import json
import random

random.seed(20240611)
T = 24
gens = {}
sched = {}
for i in range(6):
    name = f'G{i + 1:02d}'
    pmin = round(random.uniform(20, 80), 1)
    pmax = round(pmin + random.uniform(60, 200), 1)
    nseg = random.randint(2, 4)
    mws = [pmin + (pmax - pmin) * k / nseg for k in range(nseg + 1)]
    mws[-1] = pmax
    base = random.uniform(300, 900)
    slope0 = random.uniform(12, 30)
    cost = base
    pts = [{'mw': round(mws[0], 2), 'cost': round(base, 2)}]
    for k in range(1, nseg + 1):
        cost += slope0 * (1 + 0.15 * k) * (mws[k] - mws[k - 1])
        pts.append({'mw': round(mws[k], 2), 'cost': round(cost, 2)})
    hot = random.uniform(500, 1500)
    tiers = [{'lag': 1, 'cost': round(hot, 2)},
             {'lag': random.randint(3, 6), 'cost': round(hot * 1.6, 2)},
             {'lag': random.randint(8, 12), 'cost': round(hot * 2.4, 2)}]
    random.shuffle(tiers)
    on0 = random.randint(0, 1)
    gens[name] = {
        'power_output_minimum': pmin,
        'power_output_maximum': pmax,
        'unit_on_t0': on0,
        'time_up_t0': random.randint(1, 10) if on0 else 0,
        'time_down_t0': 0 if on0 else random.randint(1, 15),
        'startup': tiers,
        'piecewise_production': pts,
    }
    u = []
    state = on0
    while len(u) < T:
        L = random.randint(2, 7) if state else random.randint(1, 6)
        u.extend([state] * L)
        state = 1 - state
    u = u[:T]
    p = [round(random.uniform(pmin, pmax), 2) if x else 0.0 for x in u]
    sched[name] = {'commitment': u, 'production_MW': p}

with open('case.json', 'w') as f:
    json.dump({'time_periods': T, 'thermal_generators': gens}, f, indent=1)
with open('schedule.json', 'w') as f:
    json.dump({'time_periods': T, 'generators': sched}, f, indent=1)

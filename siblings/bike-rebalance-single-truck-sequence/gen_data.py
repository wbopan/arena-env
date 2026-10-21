import itertools
import json
import math
import random

R = 3960.0


def gc(a, b):
    p1 = math.radians(a['latitude'])
    p2 = math.radians(b['latitude'])
    dl = math.radians(b['longitude'] - a['longitude'])
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(min(1.0, math.sqrt(h)))


def best(depot, stations, cap, start, use_cap):
    n = len(stations)
    pts = stations + [depot]
    D = [[gc(a, b) for b in pts] for a in pts]
    t = [s['net_rebalancing_target'] for s in stations]
    out = None
    for perm in itertools.permutations(range(n)):
        if use_cap:
            load = start
            ok = True
            for i in perm:
                load += t[i]
                if load < 0 or load > cap:
                    ok = False
                    break
            if not ok:
                continue
        d = D[n][perm[0]] + D[perm[-1]][n] + sum(D[a][b] for a, b in zip(perm, perm[1:]))
        if out is None or d < out:
            out = d
    return out


depot = {'latitude': 41.8781, 'longitude': -87.6298}
written = False
for attempt in range(500):
    rng = random.Random(9100 + attempt)
    ids = rng.sample(range(200, 990), 8)
    targets = [rng.randint(2, 9) for _ in range(4)] + [-rng.randint(2, 9) for _ in range(4)]
    rng.shuffle(targets)
    cap = rng.randint(9, 12)
    start = rng.randint(0, 3)
    stations = [{'id': sid,
                 'latitude': round(depot['latitude'] + rng.uniform(-0.04, 0.04), 6),
                 'longitude': round(depot['longitude'] + rng.uniform(-0.05, 0.05), 6),
                 'net_rebalancing_target': t} for sid, t in zip(ids, targets)]
    end = start + sum(targets)
    if not (0 <= end <= cap):
        continue
    bc = best(depot, stations, cap, start, True)
    if bc is None:
        continue
    bu = best(depot, stations, cap, start, False)
    if bc > bu + 0.05:
        with open('truck.json', 'w') as f:
            json.dump({'vehicle_capacity': cap, 'start_load': start, 'depot': depot, 'stations': stations}, f, indent=2)
        written = True
        break
if not written:
    raise SystemExit('could not generate instance')

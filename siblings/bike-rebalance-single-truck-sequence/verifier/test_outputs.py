import csv
import itertools
import json
import math
from pathlib import Path

import pytest

WORK = Path('/root/work')
OUT = WORK / 'route.csv'
HEADER = ['position', 'station_id', 'bikes_picked_up', 'bikes_dropped_off', 'load_after_stop']


def gc(a, b):
    p1 = math.radians(a['latitude'])
    p2 = math.radians(b['latitude'])
    dl = math.radians(b['longitude'] - a['longitude'])
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 3960.0 * math.asin(min(1.0, math.sqrt(h)))


def load_data():
    return json.loads((WORK / 'truck.json').read_text())


def optimum(data):
    st = data['stations']
    n = len(st)
    pts = st + [data['depot']]
    D = [[gc(a, b) for b in pts] for a in pts]
    t = [s['net_rebalancing_target'] for s in st]
    best = None
    for perm in itertools.permutations(range(n)):
        load = data['start_load']
        ok = True
        for i in perm:
            load += t[i]
            if load < 0 or load > data['vehicle_capacity']:
                ok = False
                break
        if not ok:
            continue
        d = D[n][perm[0]] + D[perm[-1]][n] + sum(D[a][b] for a, b in zip(perm, perm[1:]))
        if best is None or d < best:
            best = d
    return best


@pytest.fixture(scope='module')
def body():
    assert OUT.exists(), 'route.csv missing'
    with OUT.open(newline='') as f:
        rows = list(csv.reader(f))
    assert rows, 'route.csv empty'
    assert [h.strip() for h in rows[0]] == HEADER, rows[0]
    return [[c.strip() for c in r] for r in rows[1:] if r and any(c.strip() for c in r)]


def num(x):
    v = float(x)
    assert abs(v - round(v)) < 1e-9, f'{x} not integer'
    return int(round(v))


def test_file_exists():
    assert OUT.exists(), 'route.csv missing'


def test_rows_and_positions(body):
    data = load_data()
    assert len(body) == len(data['stations'])
    assert all(len(r) == 5 for r in body)
    assert [num(r[0]) for r in body] == list(range(1, len(body) + 1))


def test_each_station_once_with_exact_quantities(body):
    data = load_data()
    tgt = {s['id']: s['net_rebalancing_target'] for s in data['stations']}
    ids = [num(r[1]) for r in body]
    assert sorted(ids) == sorted(tgt), ids
    for r in body:
        sid = num(r[1])
        t = tgt[sid]
        assert num(r[2]) == max(t, 0), (sid, r)
        assert num(r[3]) == max(-t, 0), (sid, r)


def test_loads_consistent_and_feasible(body):
    data = load_data()
    load = data['start_load']
    for r in body:
        load += num(r[2]) - num(r[3])
        assert num(r[4]) == load, r
        assert 0 <= load <= data['vehicle_capacity'], r


def test_distance_is_optimal(body):
    data = load_data()
    st = {s['id']: s for s in data['stations']}
    pts = [data['depot']] + [st[num(r[1])] for r in body] + [data['depot']]
    d = sum(gc(a, b) for a, b in zip(pts, pts[1:]))
    opt = optimum(data)
    assert d <= opt + 1e-6, f'route distance {d:.6f} > optimum {opt:.6f}'

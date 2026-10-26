import itertools
import json
import math
from pathlib import Path

DATA = Path('/root/work/data.json')
OUT = Path('/root/work/route.json')


def distance(a, b):
    p1, p2 = map(math.radians, (a['latitude'], b['latitude']))
    dp = p2 - p1
    dl = math.radians(b['longitude'] - a['longitude'])
    h = math.sin(dp / 2)**2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2)**2
    return 7920.0 * math.asin(min(1.0, math.sqrt(max(0.0, h))))


def expected(data):
    stations = {s['id']: s for s in data['stations']}
    ids = sorted(stations)
    best = None
    for k in range(len(ids) + 1):
        for order in itertools.permutations(ids, k):
            load = data['start_load']
            prev = data['depot']
            travel = 0.0
            for sid in order:
                s = stations[sid]
                load += s['net_rebalancing_target']
                if not 0 <= load <= data['vehicle_capacity']:
                    break
                final = s['initial_bikes'] - s['net_rebalancing_target']
                if not 0 <= final <= s['station_capacity']:
                    break
                travel += distance(prev, s)
                prev = s
            else:
                travel += distance(prev, data['depot']) if order else 0.0
                penalty = data['penalty_weight'] * sum(abs(stations[i]['net_rebalancing_target']) for i in ids if i not in order)
                cost = travel + penalty
                if best is None or cost < best[0] - 1e-9 or (abs(cost - best[0]) <= 1e-9 and order < best[1]):
                    best = (cost, order, travel, penalty)
    return best


def test_file_exists():
    assert OUT.is_file()


def test_schema():
    r = json.loads(OUT.read_text())
    assert set(r) == {'route', 'travel_distance_miles', 'unmet_penalty', 'objective'}
    assert isinstance(r['route'], list)
    assert all(isinstance(r[k], (int, float)) and not isinstance(r[k], bool) and math.isfinite(r[k]) for k in ('travel_distance_miles', 'unmet_penalty', 'objective'))


def test_route_is_feasible():
    d = json.loads(DATA.read_text())
    r = json.loads(OUT.read_text())['route']
    ids = {s['id']: s for s in d['stations']}
    assert len(r) >= 2 and r[0] == 'depot_start' and r[-1] == 'depot_end'
    assert all(type(i) is int and i in ids for i in r[1:-1])
    assert len(r[1:-1]) == len(set(r[1:-1]))
    load = d['start_load']
    for i in r[1:-1]:
        s = ids[i]
        load += s['net_rebalancing_target']
        assert 0 <= load <= d['vehicle_capacity']
        assert 0 <= s['initial_bikes'] - s['net_rebalancing_target'] <= s['station_capacity']


def test_optimal_route_and_values():
    d = json.loads(DATA.read_text())
    r = json.loads(OUT.read_text())
    cost, order, travel, penalty = expected(d)
    assert r['route'] == ['depot_start', *order, 'depot_end']
    for key, value in [('objective', cost), ('travel_distance_miles', travel), ('unmet_penalty', penalty)]:
        assert abs(r[key] - value) <= 5.1e-7

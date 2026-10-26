import itertools
import json
import math
from pathlib import Path

DATA = Path('/root/work/data.json')
OUT = Path('/root/work/assignment.json')


def miles(a, b):
    lat1, lat2 = math.radians(a['latitude']), math.radians(b['latitude'])
    h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(math.radians(b['longitude']-a['longitude'])/2)**2
    return 7920 * math.asin(min(1.0, math.sqrt(max(0.0, h))))


def route_cost(order, stations, depot):
    points = [depot] + [stations[i] for i in order] + [depot]
    return sum(miles(a, b) for a, b in zip(points, points[1:]))


def load_trace(order, vehicle, stations, capacity):
    load = vehicle['start_load']
    result = []
    for sid in order:
        s = stations[sid]
        load += s['net_rebalancing_target']
        if not 0 <= load <= capacity or not 0 <= s['initial_bikes']-s['net_rebalancing_target'] <= s['station_capacity']:
            return None
        result.append(load)
    return result


def optimum(data):
    stations = {s['id']: s for s in data['stations']}
    best = None
    for perm in itertools.permutations(sorted(stations)):
        for cut in range(1, len(perm)):
            pair = (perm[:cut], perm[cut:])
            if any(load_trace(pair[j], data['vehicles'][j], stations, data['vehicle_capacity']) is None for j in (0, 1)):
                continue
            cost = sum(route_cost(p, stations, data['depot']) for p in pair)
            if best is None or cost < best[0]-1e-9 or (abs(cost-best[0]) <= 1e-9 and pair < best[1]):
                best = (cost, pair)
    return best


def test_exists():
    assert OUT.is_file()


def test_schema():
    r = json.loads(OUT.read_text())
    assert set(r) == {'vehicles', 'travel_distance_miles'}
    assert isinstance(r['vehicles'], list) and len(r['vehicles']) == 2
    assert type(r['travel_distance_miles']) in (int, float) and math.isfinite(r['travel_distance_miles'])
    for v in r['vehicles']:
        assert set(v) == {'vehicle_id', 'route', 'loads_after_stops', 'end_load'}


def test_assignment_and_loads():
    d = json.loads(DATA.read_text())
    r = json.loads(OUT.read_text())
    stations = {s['id']: s for s in d['stations']}
    all_ids = []
    for actual, vehicle in zip(r['vehicles'], d['vehicles']):
        route = actual['route']
        assert actual['vehicle_id'] == vehicle['vehicle_id']
        assert route[0] == 'depot_start' and route[-1] == 'depot_end' and len(route) >= 3
        ids = route[1:-1]
        assert all(type(i) is int and i in stations for i in ids)
        trace = load_trace(ids, vehicle, stations, d['vehicle_capacity'])
        assert trace is not None
        assert actual['loads_after_stops'] == trace
        assert actual['end_load'] == trace[-1]
        all_ids.extend(ids)
    assert sorted(all_ids) == sorted(stations)


def test_minimum_distance_and_tiebreak():
    d = json.loads(DATA.read_text())
    r = json.loads(OUT.read_text())
    value, paths = optimum(d)
    assert tuple(tuple(v['route'][1:-1]) for v in r['vehicles']) == paths
    assert abs(r['travel_distance_miles'] - value) <= 5.1e-7

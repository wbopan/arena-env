import json
import math
from pathlib import Path

DATA = Path('/root/work/data.json')
OUT = Path('/root/work/service.json')


def length(data):
    stations = {s['id']: s for s in data['stations']}
    points = [data['depot']] + [stations[i] for i in data['route']] + [data['depot']]
    result = 0.0
    for a, b in zip(points, points[1:]):
        x, y = math.radians(a['latitude']), math.radians(b['latitude'])
        h = math.sin((y-x)/2)**2 + math.cos(x)*math.cos(y)*math.sin(math.radians(b['longitude']-a['longitude'])/2)**2
        result += 7920 * math.asin(min(1.0, math.sqrt(max(0, h))))
    return result


def best_service(data):
    stations = {s['id']: s for s in data['stations']}
    states = {data['start_load']: (0.0, ())}
    for sid in data['route']:
        s = stations[sid]
        next_states = {}
        for load, (cost, sequence) in states.items():
            for q in range(s['initial_bikes']-s['station_capacity'], s['initial_bikes']+1):
                new_load = load + q
                if not 0 <= new_load <= data['vehicle_capacity']:
                    continue
                candidate = (cost + s['penalty_weight']*abs(s['net_rebalancing_target']-q) + data['handling_cost_per_bike']*abs(q), sequence+(q,))
                old = next_states.get(new_load)
                if old is None or candidate[0] < old[0]-1e-9 or (abs(candidate[0]-old[0]) <= 1e-9 and candidate[1] < old[1]):
                    next_states[new_load] = candidate
        states = next_states
    return states[data['required_end_load']]


def test_exists():
    assert OUT.is_file()


def test_schema():
    r = json.loads(OUT.read_text())
    assert set(r) == {'route', 'net_pickups', 'loads_after_stops', 'travel_distance_miles', 'unmet_penalty', 'handling_cost', 'objective'}
    for k in ('travel_distance_miles', 'unmet_penalty', 'handling_cost', 'objective'):
        assert type(r[k]) in (int, float) and math.isfinite(r[k])


def test_route_and_capacity():
    d = json.loads(DATA.read_text())
    r = json.loads(OUT.read_text())
    assert r['route'] == ['depot_start', *d['route'], 'depot_end']
    assert len(r['net_pickups']) == len(r['loads_after_stops']) == len(d['route'])
    stations = {s['id']: s for s in d['stations']}
    load = d['start_load']
    for sid, q, reported in zip(d['route'], r['net_pickups'], r['loads_after_stops']):
        assert type(q) is int and type(reported) is int
        s = stations[sid]
        load += q
        assert 0 <= load <= d['vehicle_capacity']
        assert 0 <= s['initial_bikes']-q <= s['station_capacity']
        assert reported == load
    assert load == d['required_end_load']


def test_optimal_service_and_costs():
    d = json.loads(DATA.read_text())
    r = json.loads(OUT.read_text())
    _, optimum = best_service(d)
    assert r['net_pickups'] == list(optimum)
    stations = {s['id']: s for s in d['stations']}
    penalty = sum(stations[i]['penalty_weight']*abs(stations[i]['net_rebalancing_target']-q) for i, q in zip(d['route'], optimum))
    handling = d['handling_cost_per_bike']*sum(abs(q) for q in optimum)
    travel = length(d)
    for key, expected in [('unmet_penalty', penalty), ('handling_cost', handling), ('travel_distance_miles', travel), ('objective', penalty+handling+travel)]:
        assert abs(r[key]-expected) <= 5.1e-7

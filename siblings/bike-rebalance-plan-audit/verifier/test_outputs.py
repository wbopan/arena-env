import json
import math
from pathlib import Path

import pytest

WORK = Path('/root/work')
OUT = WORK / 'audit.json'
TOL = 1e-3


def gc(a, b):
    p1 = math.radians(a['latitude'])
    p2 = math.radians(b['latitude'])
    dl = math.radians(b['longitude'] - a['longitude'])
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 3960.0 * math.asin(min(1.0, math.sqrt(h)))


def expected():
    data = json.loads((WORK / 'data.json').read_text())
    plan = json.loads((WORK / 'plan.json').read_text())
    st = {s['id']: s for s in data['stations']}
    cap = data['vehicle_capacity']
    pick = {k: 0 for k in st}
    drop = {k: 0 for k in st}
    vehs = []
    for v in plan['vehicles']:
        pts = [data['depot']] + [st[s['station_id']] for s in v['stops']] + [data['depot']]
        dist = sum(gc(a, b) for a, b in zip(pts, pts[1:]))
        load = v['start_load']
        loads = [load]
        for s in v['stops']:
            load += s['bikes_picked_up'] - s['bikes_dropped_off']
            loads.append(load)
            pick[s['station_id']] += s['bikes_picked_up']
            drop[s['station_id']] += s['bikes_dropped_off']
        vehs.append({'vehicle_id': v['vehicle_id'], 'distance_miles': dist, 'min_load': min(loads),
                     'max_load': max(loads), 'end_load': loads[-1],
                     'capacity_ok': bool(min(loads) >= 0 and max(loads) <= cap)})
    stas = []
    for s in data['stations']:
        k = s['id']
        fin = s['initial_bikes'] - pick[k] + drop[k]
        stas.append({'station_id': k, 'total_bikes_picked_up': pick[k], 'total_bikes_dropped_off': drop[k],
                     'final_inventory': fin, 'inventory_ok': bool(0 <= fin <= s['station_capacity']),
                     'unmet_rebalancing_amount': abs(s['net_rebalancing_target'] - (pick[k] - drop[k]))})
    travel = sum(v['distance_miles'] for v in vehs)
    unmet = sum(s['unmet_rebalancing_amount'] for s in stas)
    pen = data['penalty_weight'] * unmet
    summ = {'travel_distance_miles': travel, 'total_unmet_rebalancing_amount': unmet,
            'unmet_rebalancing_penalty': pen, 'objective': travel + pen,
            'all_feasible': all(v['capacity_ok'] for v in vehs) and all(s['inventory_ok'] for s in stas)}
    return vehs, stas, summ


@pytest.fixture(scope='module')
def report():
    assert OUT.exists(), 'audit.json missing'
    return json.loads(OUT.read_text())


def test_file_exists_and_parses():
    assert OUT.exists(), 'audit.json missing'
    assert isinstance(json.loads(OUT.read_text()), dict)


def test_schema(report):
    vehs, stas, _ = expected()
    for key in ('vehicles', 'stations', 'summary'):
        assert key in report, key
    assert [int(v['vehicle_id']) for v in report['vehicles']] == [v['vehicle_id'] for v in vehs]
    assert [int(s['station_id']) for s in report['stations']] == [s['station_id'] for s in stas]


def test_vehicle_values(report):
    vehs, _, _ = expected()
    for got, exp in zip(report['vehicles'], vehs):
        vid = exp['vehicle_id']
        assert abs(float(got['distance_miles']) - exp['distance_miles']) <= TOL, (vid, got['distance_miles'], exp['distance_miles'])
        for k in ('min_load', 'max_load', 'end_load'):
            assert abs(float(got[k]) - exp[k]) < 1e-6, (vid, k, got[k], exp[k])
        assert isinstance(got['capacity_ok'], bool) and got['capacity_ok'] == exp['capacity_ok'], vid


def test_station_values(report):
    _, stas, _ = expected()
    for got, exp in zip(report['stations'], stas):
        sid = exp['station_id']
        for k in ('total_bikes_picked_up', 'total_bikes_dropped_off', 'final_inventory', 'unmet_rebalancing_amount'):
            assert abs(float(got[k]) - exp[k]) < 1e-6, (sid, k, got[k], exp[k])
        assert isinstance(got['inventory_ok'], bool) and got['inventory_ok'] == exp['inventory_ok'], sid


def test_summary(report):
    _, _, s = expected()
    got = report['summary']
    for k in ('travel_distance_miles', 'unmet_rebalancing_penalty', 'objective'):
        assert abs(float(got[k]) - s[k]) <= TOL, (k, got[k], s[k])
    assert abs(float(got['total_unmet_rebalancing_amount']) - s['total_unmet_rebalancing_amount']) < 1e-6
    assert isinstance(got['all_feasible'], bool) and got['all_feasible'] == s['all_feasible']

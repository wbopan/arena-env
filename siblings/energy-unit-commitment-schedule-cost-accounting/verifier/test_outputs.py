import json
import os

import pytest

W = '/root/work'
OUT = os.path.join(W, 'cost_report.json')
TOL = 0.05


def interp(points, x):
    pts = sorted((float(a['mw']), float(a['cost'])) for a in points)
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (x - x0) * (y1 - y0) / (x1 - x0)
    raise ValueError('outside curve')


def expected():
    with open(os.path.join(W, 'case.json')) as f:
        case = json.load(f)
    with open(os.path.join(W, 'schedule.json')) as f:
        sch = json.load(f)['generators']
    T = int(case['time_periods'])
    res = []
    for name, g in case['thermal_generators'].items():
        u = sch[name]['commitment']
        p = sch[name]['production_MW']
        tiers = sorted((int(s['lag']), float(s['cost'])) for s in g['startup'])
        prev = int(g['unit_on_t0'])
        off = 0 if prev == 1 else int(g['time_down_t0'])
        pc = 0.0
        sc = 0.0
        ns = 0
        for t in range(T):
            if int(u[t]) == 1:
                pc += interp(g['piecewise_production'], float(p[t]))
                if prev == 0:
                    ns += 1
                    c = tiers[0][1]
                    for lag, cost in tiers:
                        if lag <= off:
                            c = cost
                    sc += c
                off = 0
            else:
                off += 1
            prev = int(u[t])
        res.append({'name': name, 'num_startups': ns, 'production_cost': pc, 'startup_cost': sc})
    return res


@pytest.fixture(scope='module')
def report():
    assert os.path.exists(OUT), 'cost_report.json missing'
    with open(OUT) as f:
        data = json.load(f)
    assert isinstance(data, dict)
    return data


@pytest.fixture(scope='module')
def exp():
    return expected()


def test_schema_and_order(report, exp):
    for k in ('generators', 'total_production_cost', 'total_startup_cost', 'total_cost'):
        assert k in report, f'missing {k}'
    gens = report['generators']
    assert [g['name'] for g in gens] == [e['name'] for e in exp]
    for g in gens:
        for k in ('num_startups', 'production_cost', 'startup_cost', 'total_cost'):
            assert k in g, f'{g.get("name")} missing {k}'


def test_num_startups(report, exp):
    for g, e in zip(report['generators'], exp):
        assert int(g['num_startups']) == e['num_startups'], g['name']


def test_production_cost(report, exp):
    for g, e in zip(report['generators'], exp):
        assert abs(float(g['production_cost']) - e['production_cost']) <= TOL, g['name']


def test_startup_cost(report, exp):
    for g, e in zip(report['generators'], exp):
        assert abs(float(g['startup_cost']) - e['startup_cost']) <= TOL, g['name']
        assert abs(float(g['total_cost']) - e['startup_cost'] - e['production_cost']) <= TOL, g['name']


def test_system_totals(report, exp):
    tp = sum(e['production_cost'] for e in exp)
    ts = sum(e['startup_cost'] for e in exp)
    assert abs(float(report['total_production_cost']) - tp) <= TOL
    assert abs(float(report['total_startup_cost']) - ts) <= TOL
    assert abs(float(report['total_cost']) - tp - ts) <= TOL

import json
import os

import pytest

WORK = '/root/work'
OUT = os.path.join(WORK, 'dispatch.json')
NET = os.path.join(WORK, 'network.json')


def solve_ed():
    with open(NET) as f:
        d = json.load(f)
    gens = d['gen']
    gc = d['gencost']
    load = sum(float(b[2]) for b in d['bus'])
    on = [i for i, g in enumerate(gens) if int(g[7]) == 1]

    def out(i, lam):
        c2, c1 = float(gc[i][4]), float(gc[i][5])
        p = (lam - c1) / (2 * c2)
        return min(max(p, float(gens[i][9])), float(gens[i][8]))

    lo = min(float(gc[i][5]) + 2 * float(gc[i][4]) * float(gens[i][9]) for i in on) - 1
    hi = max(float(gc[i][5]) + 2 * float(gc[i][4]) * float(gens[i][8]) for i in on) + 1
    for _ in range(300):
        lam = 0.5 * (lo + hi)
        if sum(out(i, lam) for i in on) < load:
            lo = lam
        else:
            hi = lam
    lam = 0.5 * (lo + hi)
    P = [0.0] * len(gens)
    for i in on:
        P[i] = out(i, lam)
    cost = sum(float(gc[i][4]) * P[i] ** 2 + float(gc[i][5]) * P[i] + float(gc[i][6]) for i in on)
    margin = sum(float(gens[i][8]) - P[i] for i in on)
    return {'P': P, 'bus': [int(g[0]) for g in gens], 'lam': lam, 'cost': cost,
            'load': load, 'margin': margin}


@pytest.fixture(scope='module')
def rep():
    assert os.path.exists(OUT), 'dispatch.json missing'
    with open(OUT) as f:
        return json.load(f)


@pytest.fixture(scope='module')
def exp():
    return solve_ed()


def test_schema(rep):
    for k in ['generators', 'system_lambda', 'total_cost', 'load_MW', 'spinning_margin_MW']:
        assert k in rep, k
    for g in rep['generators']:
        for k in ['id', 'bus', 'output_MW']:
            assert k in g


def test_generator_outputs(rep, exp):
    gl = rep['generators']
    assert len(gl) == len(exp['P'])
    for i, g in enumerate(gl):
        assert int(g['id']) == i + 1
        assert int(g['bus']) == exp['bus'][i]
        assert abs(float(g['output_MW']) - exp['P'][i]) <= 0.05, (i, g, exp['P'][i])


def test_balance_and_load(rep, exp):
    assert abs(float(rep['load_MW']) - exp['load']) <= 0.02
    tot = sum(float(g['output_MW']) for g in rep['generators'])
    assert abs(tot - exp['load']) <= 0.1


def test_lambda(rep, exp):
    assert abs(float(rep['system_lambda']) - exp['lam']) <= 0.01


def test_cost_and_margin(rep, exp):
    assert abs(float(rep['total_cost']) - exp['cost']) <= 0.5
    assert abs(float(rep['spinning_margin_MW']) - exp['margin']) <= 0.1

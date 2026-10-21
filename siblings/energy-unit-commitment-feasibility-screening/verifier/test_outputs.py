import csv
import json
import os

import pytest

W = '/root/work'
OUT = os.path.join(W, 'checks.csv')
COLS = ['schedule', 'demand_balance', 'generator_limits', 'spinning_reserve', 'ramping', 'minimum_up_down', 'overall']
E = 1e-6


def expected():
    with open(os.path.join(W, 'case.json')) as f:
        case = json.load(f)
    with open(os.path.join(W, 'candidates.json')) as f:
        cands = json.load(f)['schedules']
    T = int(case['time_periods'])
    gens = case['thermal_generators']
    out = []
    for s in cands:
        U = s['commitment']
        P = s['production_MW']
        db = all(abs(sum(P[n][t] for n in gens) - case['demand'][t]) <= 0.01 for t in range(T))
        sr = all(sum(gens[n]['power_output_maximum'] - P[n][t] for n in gens if U[n][t] == 1)
                 >= case['reserves'][t] - 0.01 for t in range(T))
        gl = rp = mud = True
        for n, g in gens.items():
            u = U[n]
            p = P[n]
            for t in range(T):
                if u[t] not in (0, 1):
                    gl = False
                if u[t] == 1:
                    if p[t] < g['power_output_minimum'] - E or p[t] > g['power_output_maximum'] + E:
                        gl = False
                elif abs(p[t]) > E:
                    gl = False
                pu = g['unit_on_t0'] if t == 0 else u[t - 1]
                pp = g['power_output_t0'] if t == 0 else p[t - 1]
                if pu == 1 and u[t] == 1:
                    if p[t] - pp > g['ramp_up_limit'] + E or pp - p[t] > g['ramp_down_limit'] + E:
                        rp = False
                if u[t] != pu:
                    L = g['time_up_minimum'] if u[t] == 1 else g['time_down_minimum']
                    if any(u[k] != u[t] for k in range(t, min(T, t + L))):
                        mud = False
            if g['unit_on_t0'] == 1:
                need, st = g['time_up_minimum'] - g['time_up_t0'], 1
            else:
                need, st = g['time_down_minimum'] - g['time_down_t0'], 0
            if any(u[k] != st for k in range(min(T, max(need, 0)))):
                mud = False
        vals = [db, gl, sr, rp, mud]
        f = lambda b: 'pass' if b else 'fail'
        out.append([s['id']] + [f(v) for v in vals] + [f(all(vals))])
    return out


@pytest.fixture(scope='module')
def rows():
    assert os.path.exists(OUT), 'checks.csv missing'
    with open(OUT, newline='') as fh:
        r = [[c.strip() for c in row] for row in csv.reader(fh) if row]
    return r


@pytest.fixture(scope='module')
def exp():
    return expected()


def test_header(rows):
    assert rows[0] == COLS


def test_rows_and_values(rows, exp):
    body = rows[1:]
    assert [r[0] for r in body] == [e[0] for e in exp]
    for r in body:
        assert len(r) == len(COLS)
        assert all(v in ('pass', 'fail') for v in r[1:])


def _col(rows, exp, name):
    i = COLS.index(name)
    for r, e in zip(rows[1:], exp):
        assert r[i] == e[i], f'{e[0]} {name}: got {r[i]}, expected {e[i]}'


def test_balance_and_limits(rows, exp):
    _col(rows, exp, 'demand_balance')
    _col(rows, exp, 'generator_limits')


def test_reserve_and_ramping(rows, exp):
    _col(rows, exp, 'spinning_reserve')
    _col(rows, exp, 'ramping')


def test_minimum_up_down(rows, exp):
    _col(rows, exp, 'minimum_up_down')


def test_overall(rows, exp):
    _col(rows, exp, 'overall')

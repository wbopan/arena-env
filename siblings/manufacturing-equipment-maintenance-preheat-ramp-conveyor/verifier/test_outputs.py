import json
import os

import pandas as pd
import pytest

W = '/root/work'
OUT = os.path.join(W, 'output', 'ramp_conveyor.json')
TOL = 0.011

# Current-revision values stated in /root/work/handbook.md
TMIN, TMAX = 100.0, 150.0
LIMIT = 2.0
OVEN = {'OV-A': 360.0, 'OV-B': 420.0, 'OV-C': 300.0}
MIN_DWELL = {'THIN': 150.0, 'STD': 180.0, 'THICK': 220.0}
MAX_DWELL = 330.0
KEYS = {'run_id', 'tc_id', 'max_preheat_ramp_c_per_s', 'ramp_ok', 'speed_min_cm_min',
        'speed_max_cm_min', 'actual_speed_cm_min', 'speed_ok'}


def max_ramp(t, y):
    best = None
    for i in range(1, len(t)):
        dt = t[i] - t[i - 1]
        if dt <= 0:
            continue
        if TMIN <= y[i - 1] <= TMAX and TMIN <= y[i] <= TMAX:
            s = (y[i] - y[i - 1]) / dt
            if best is None or s > best:
                best = s
    return best


@pytest.fixture(scope='module')
def exp():
    mes = pd.read_csv(os.path.join(W, 'mes_log.csv'), dtype={'run_id': str})
    tc = pd.read_csv(os.path.join(W, 'thermocouples.csv'), dtype={'run_id': str, 'tc_id': str})
    res = {}
    for _, r in mes.iterrows():
        g = tc[tc['run_id'] == r['run_id']]
        best = None
        for tcid in sorted(g['tc_id'].unique()):
            h = g[g['tc_id'] == tcid].sort_values('time_s', kind='mergesort')
            m = max_ramp(h['time_s'].to_numpy(float), h['temp_c'].to_numpy(float))
            if m is not None and (best is None or m > best[1]):
                best = (tcid, m)
        L = OVEN[r['oven_id']]
        smin = L * 60.0 / MAX_DWELL
        smax = L * 60.0 / MIN_DWELL[r['board_family']]
        act = float(r['conveyor_speed_cm_min'])
        res[r['run_id']] = {
            'tc': None if best is None else best[0],
            'ramp': None if best is None else best[1],
            'ramp_ok': False if best is None else round(best[1], 2) <= LIMIT,
            'smin': smin, 'smax': smax, 'act': act,
            'speed_ok': round(smin, 2) <= act <= round(smax, 2),
        }
    return res


@pytest.fixture(scope='module')
def out():
    assert os.path.exists(OUT), f'missing output file {OUT}'
    with open(OUT) as f:
        return json.load(f)


def runs_by_id(out):
    return {str(r['run_id']): r for r in out['runs']}


def test_top_level(out):
    assert isinstance(out, dict) and 'runs' in out and 'ramp_limit_c_per_s' in out
    assert abs(float(out['ramp_limit_c_per_s']) - LIMIT) <= TOL
    for r in out['runs']:
        assert KEYS.issubset(r.keys()), f'run entry missing keys: {KEYS - set(r.keys())}'


def test_runs_sorted_complete(out, exp):
    ids = [str(r['run_id']) for r in out['runs']]
    assert ids == sorted(exp.keys()), f'expected {sorted(exp.keys())}, got {ids}'


def test_ramp_sensor_and_value(out, exp):
    rows = runs_by_id(out)
    for rid, e in exp.items():
        r = rows[rid]
        if e['tc'] is None:
            assert r['tc_id'] is None and r['max_preheat_ramp_c_per_s'] is None, rid
        else:
            assert str(r['tc_id']) == e['tc'], f'{rid}: expected {e["tc"]}, got {r["tc_id"]}'
            assert abs(float(r['max_preheat_ramp_c_per_s']) - e['ramp']) <= TOL, \
                f'{rid}: expected {round(e["ramp"], 2)}, got {r["max_preheat_ramp_c_per_s"]}'


def test_ramp_ok(out, exp):
    rows = runs_by_id(out)
    for rid, e in exp.items():
        assert rows[rid]['ramp_ok'] is e['ramp_ok'], f'{rid}: ramp_ok should be {e["ramp_ok"]}'


def test_speed_limits(out, exp):
    rows = runs_by_id(out)
    for rid, e in exp.items():
        r = rows[rid]
        assert abs(float(r['speed_min_cm_min']) - e['smin']) <= TOL, rid
        assert abs(float(r['speed_max_cm_min']) - e['smax']) <= TOL, rid
        assert abs(float(r['actual_speed_cm_min']) - e['act']) <= TOL, rid


def test_speed_ok(out, exp):
    rows = runs_by_id(out)
    for rid, e in exp.items():
        assert rows[rid]['speed_ok'] is e['speed_ok'], f'{rid}: speed_ok should be {e["speed_ok"]}'

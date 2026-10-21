import csv
import os

import pandas as pd
import pytest
import yaml

W = '/root/work'
OUT = os.path.join(W, 'output', 'tal_report.csv')
COLS = ['run_id', 'alloy', 'liquidus_c', 'tc_id', 'tal_s', 'tal_min_s', 'tal_max_s', 'status']
TOL = 0.011


def tal_above(t, y, thr):
    total = 0.0
    for i in range(1, len(t)):
        t0, t1, y0, y1 = t[i - 1], t[i], y[i - 1], y[i]
        if t1 <= t0:
            continue
        a0, a1 = y0 > thr, y1 > thr
        if a0 and a1:
            total += t1 - t0
        elif a0 != a1:
            tc = t0 + (thr - y0) / (y1 - y0) * (t1 - t0)
            total += (t1 - tc) if a1 else (tc - t0)
    return total


@pytest.fixture(scope='module')
def exp():
    with open(os.path.join(W, 'spec.yaml')) as f:
        spec = yaml.safe_load(f)
    alloys = {a['name']: a for a in spec['alloys']}
    mes = pd.read_csv(os.path.join(W, 'mes_log.csv'), dtype={'run_id': str})
    tc = pd.read_csv(os.path.join(W, 'thermocouples.csv'), dtype={'run_id': str, 'tc_id': str})
    res = {}
    for rid, alloy in zip(mes['run_id'], mes['alloy']):
        a = alloys[alloy]
        liq = float(a['liquidus_c'])
        lo, hi = float(a['tal_min_s']), float(a['tal_max_s'])
        g = tc[tc['run_id'] == rid]
        best = None
        for tcid in sorted(g['tc_id'].unique()):
            h = g[g['tc_id'] == tcid].sort_values('time_s', kind='mergesort')
            v = tal_above(h['time_s'].to_numpy(float), h['temp_c'].to_numpy(float), liq)
            if best is None or v < best[1]:
                best = (tcid, v)
        if best is None:
            status = 'non-compliant'
        else:
            r = round(best[1], 2)
            status = 'compliant' if lo <= r <= hi else 'non-compliant'
        res[rid] = {'alloy': alloy, 'liq': liq, 'lo': lo, 'hi': hi,
                    'tc': None if best is None else best[0],
                    'tal': None if best is None else best[1], 'status': status}
    return res


@pytest.fixture(scope='module')
def out():
    assert os.path.exists(OUT), f'missing output file {OUT}'
    with open(OUT, newline='') as f:
        rd = csv.DictReader(f)
        header = rd.fieldnames
        data = list(rd)
    return header, data


def by_id(out):
    return {r['run_id'].strip(): r for r in out[1]}


def test_header(out):
    assert out[0] == COLS, f'header must be {COLS}, got {out[0]}'


def test_runs_sorted_complete(out, exp):
    ids = [r['run_id'].strip() for r in out[1]]
    assert ids == sorted(exp.keys()), f'expected rows {sorted(exp.keys())}, got {ids}'


def test_spec_fields(out, exp):
    rows = by_id(out)
    for rid, e in exp.items():
        r = rows[rid]
        assert r['alloy'].strip() == e['alloy']
        assert abs(float(r['liquidus_c']) - e['liq']) <= TOL, rid
        assert abs(float(r['tal_min_s']) - e['lo']) <= TOL, rid
        assert abs(float(r['tal_max_s']) - e['hi']) <= TOL, rid


def test_worst_case_sensor(out, exp):
    rows = by_id(out)
    for rid, e in exp.items():
        got = rows[rid]['tc_id'].strip()
        if e['tc'] is None:
            assert got == '', f'{rid}: expected empty tc_id'
        else:
            assert got == e['tc'], f'{rid}: expected {e["tc"]}, got {got}'


def test_tal_values(out, exp):
    rows = by_id(out)
    for rid, e in exp.items():
        got = rows[rid]['tal_s'].strip()
        if e['tal'] is None:
            assert got == '', f'{rid}: expected empty tal_s'
        else:
            assert abs(float(got) - e['tal']) <= TOL, f'{rid}: expected {round(e["tal"], 2)}, got {got}'


def test_status(out, exp):
    rows = by_id(out)
    for rid, e in exp.items():
        assert rows[rid]['status'].strip() == e['status'], f'{rid}: expected {e["status"]}'

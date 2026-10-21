import csv
import math
import os

import pandas as pd
import pytest

W = '/root/work'
OUT = os.path.join(W, 'gl_points.csv')
P = {
    ('SBD', 'M', 'Raw'): (1199.72839, 1025.18162, 0.009210),
    ('SBD', 'M', 'Single'): (1236.25115, 1449.21864, 0.01644),
    ('SBD', 'F', 'Raw'): (610.32796, 1045.59282, 0.03048),
    ('SBD', 'F', 'Single'): (758.63878, 949.31382, 0.02435),
    ('B', 'M', 'Raw'): (320.98041, 281.40258, 0.01008),
    ('B', 'M', 'Single'): (381.22073, 733.79378, 0.02398),
    ('B', 'F', 'Raw'): (142.40398, 442.52671, 0.04724),
    ('B', 'F', 'Single'): (221.82209, 357.00377, 0.02937),
}


def expected():
    df = pd.read_excel(os.path.join(W, 'meet.xlsx'), sheet_name='Results')
    res = {}
    for _, r in df.iterrows():
        def g(c):
            x = r[c]
            return float(x) if pd.notna(x) else 0.0
        sq, bp, dl = g('Best3SquatKg'), g('Best3BenchKg'), g('Best3DeadliftKg')
        ev = str(r['Event'])
        if ev == 'SBD':
            tot = sq + bp + dl if min(sq, bp, dl) > 0 else 0.0
        else:
            tot = bp if bp > 0 else 0.0
        sex = 'F' if r['Sex'] == 'F' else 'M'
        eq = 'Raw' if r['Equipment'] in ('Raw', 'Wraps') else 'Single'
        a, b, c = P[(ev, sex, eq)]
        bw = float(r['BodyweightKg'])
        gl = 0.0
        if bw >= 35 and tot > 0:
            den = a - b * math.exp(-c * bw)
            if den != 0:
                gl = tot * max(0.0, 100.0 / den)
        res[str(r['Name'])] = (ev, tot, gl)
    return res


@pytest.fixture
def rows():
    assert os.path.exists(OUT)
    with open(OUT, newline='') as f:
        return list(csv.DictReader(f))


def test_file_exists():
    assert os.path.isfile(OUT)


def test_header():
    with open(OUT, newline='') as f:
        header = next(csv.reader(f))
    assert [h.strip() for h in header] == ['Name', 'Event', 'TotalKg', 'GLPoints']


def test_all_lifters_present(rows):
    exp = expected()
    names = [r['Name'] for r in rows]
    assert len(names) == len(exp)
    assert set(names) == set(exp)


def test_totals_and_events(rows):
    exp = expected()
    for r in rows:
        ev, tot, _ = exp[r['Name']]
        assert r['Event'] == ev, r['Name']
        assert abs(float(r['TotalKg']) - tot) <= 0.051, r['Name']


def test_gl_points(rows):
    exp = expected()
    for r in rows:
        gl = exp[r['Name']][2]
        assert abs(float(r['GLPoints']) - gl) <= 0.011, (r['Name'], r['GLPoints'], gl)


def test_sort_order(rows):
    keys = [(-round(float(r['GLPoints']), 2), r['Name']) for r in rows]
    assert keys == sorted(keys)

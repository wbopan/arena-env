import csv
import functools
import os

import numpy as np
import pytest

INP = '/root/work/stars_lc.csv'
OUT = '/root/work/rotation.csv'
FREQS = 0.05 + 0.0005 * np.arange(3901)


@functools.lru_cache(maxsize=1)
def reference():
    data = {}
    with open(INP) as fh:
        for r in csv.DictReader(fh):
            if int(r['quality']) != 0:
                continue
            data.setdefault(r['star_id'], ([], []))
            data[r['star_id']][0].append(float(r['time']))
            data[r['star_id']][1].append(float(r['flux']))
    res = {}
    for sid, (t, y) in data.items():
        t = np.asarray(t)
        y = np.asarray(y)
        tss = np.sum((y - y.mean()) ** 2)
        best = -np.inf
        bi = 0
        bc = None
        for i, f in enumerate(FREQS):
            X = np.column_stack([np.sin(2 * np.pi * f * t), np.cos(2 * np.pi * f * t), np.ones_like(t)])
            coef = np.linalg.lstsq(X, y, rcond=None)[0]
            p = 1 - np.sum((y - X @ coef) ** 2) / tss
            if p > best:
                best, bi, bc = p, i, coef
        res[sid] = (1.0 / FREQS[bi], float(np.hypot(bc[0], bc[1])))
    return res


def read_out():
    with open(OUT) as fh:
        return list(csv.DictReader(fh))


def test_file_exists():
    assert os.path.exists(OUT), 'rotation.csv not found'


def test_header():
    if not os.path.exists(OUT):
        pytest.skip('missing')
    with open(OUT) as fh:
        assert fh.readline().strip() == 'star_id,period_days,amplitude'


def test_star_rows():
    if not os.path.exists(OUT):
        pytest.skip('missing')
    ids = [r['star_id'] for r in read_out()]
    assert ids == sorted(reference().keys())


def test_periods():
    if not os.path.exists(OUT):
        pytest.skip('missing')
    ref = reference()
    for r in read_out():
        exp = ref[r['star_id']][0]
        got = float(r['period_days'])
        assert abs(got - exp) <= 2e-4, (r['star_id'], got, exp)


def test_amplitudes():
    if not os.path.exists(OUT):
        pytest.skip('missing')
    ref = reference()
    for r in read_out():
        exp = ref[r['star_id']][1]
        got = float(r['amplitude'])
        assert abs(got - exp) <= 5e-5, (r['star_id'], got, exp)

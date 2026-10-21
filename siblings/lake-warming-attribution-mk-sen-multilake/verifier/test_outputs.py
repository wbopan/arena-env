import json
import math
import os

import numpy as np
import pandas as pd
import pytest
from scipy.stats import norm

OUT = '/root/work/trend_summary.json'
INP = '/root/work/lake_temps.csv'


def expected():
    df = pd.read_csv(INP).dropna(subset=['temp_c'])
    res = {}
    for lid, g in df.groupby('lake_id'):
        g = g.sort_values('year')
        t = g['year'].to_numpy(float)
        x = g['temp_c'].to_numpy(float)
        n = len(x)
        s = 0.0
        slopes = []
        for i in range(n - 1):
            for j in range(i + 1, n):
                s += np.sign(x[j] - x[i])
                slopes.append((x[j] - x[i]) / (t[j] - t[i]))
        _, c = np.unique(x, return_counts=True)
        var = (n * (n - 1) * (2 * n + 5) - np.sum(c * (c - 1) * (2 * c + 5))) / 18.0
        if s > 0:
            z = (s - 1) / math.sqrt(var)
        elif s < 0:
            z = (s + 1) / math.sqrt(var)
        else:
            z = 0.0
        p = 2 * (1 - norm.cdf(abs(z)))
        if p < 0.05 and z > 0:
            tr = 'increasing'
        elif p < 0.05 and z < 0:
            tr = 'decreasing'
        else:
            tr = 'no trend'
        res[str(lid)] = {'n': n, 'sen_slope': float(np.median(slopes)), 'p_value': float(p), 'trend': tr}
    return res


@pytest.fixture(scope='module')
def out():
    assert os.path.exists(OUT), 'trend_summary.json not found'
    with open(OUT) as f:
        return json.load(f)


@pytest.fixture(scope='module')
def exp():
    return expected()


def test_keys(out, exp):
    assert isinstance(out, dict)
    assert set(out.keys()) == set(exp.keys())
    for k in exp:
        for fld in ('n', 'sen_slope', 'p_value', 'trend'):
            assert fld in out[k], f'{k} missing {fld}'


def test_n(out, exp):
    for k, e in exp.items():
        assert int(out[k]['n']) == e['n'], k


def test_sen_slope(out, exp):
    for k, e in exp.items():
        assert abs(float(out[k]['sen_slope']) - e['sen_slope']) <= 2e-4, k


def test_p_value(out, exp):
    for k, e in exp.items():
        assert abs(float(out[k]['p_value']) - e['p_value']) <= 1e-3, k


def test_trend(out, exp):
    for k, e in exp.items():
        assert out[k]['trend'] == e['trend'], k

import json
import os

import numpy as np
import pandas as pd
import pytest

WORK = '/root/work'
OUT = os.path.join(WORK, 'step_metrics.json')
KEYS = ['RiseTime', 'SettlingTime', 'Overshoot_pct', 'SteadyStateError']


def compute_expected():
    df = pd.read_csv(os.path.join(WORK, 'flights.csv'))
    with open(os.path.join(WORK, 'targets.json')) as f:
        targets = json.load(f)
    res = {}
    for fid, tgt in targets.items():
        g = df[df['flight_id'] == int(fid)].sort_values('t')
        t = g['t'].to_numpy(dtype=float)
        p = g[['x', 'y', 'z']].to_numpy(dtype=float)
        d = np.sqrt(((p - np.asarray(tgt, dtype=float)) ** 2).sum(axis=1))
        d0 = d[0]
        if d0 < 1e-6:
            res[fid] = {k: 0.0 for k in KEYS}
            continue
        r = np.nonzero(d <= 0.1 * d0)[0]
        rise = float(t[r[0]]) if r.size else None
        s = np.nonzero(d > 0.02 * d0)[0]
        settle = float(t[s[-1]]) if s.size else 0.0
        e = np.nonzero(d <= 0.02 * d0)[0]
        ov = float(d[e[0]:].max() / d0 * 100.0) if e.size else 0.0
        res[fid] = {'RiseTime': rise, 'SettlingTime': settle,
                    'Overshoot_pct': ov, 'SteadyStateError': float(d[-1])}
    return res


@pytest.fixture(scope='module')
def expected():
    return compute_expected()


@pytest.fixture(scope='module')
def actual():
    assert os.path.isfile(OUT), 'missing step_metrics.json'
    with open(OUT) as f:
        return json.load(f)


def _check(actual, expected, key, tol):
    for fid, m in expected.items():
        a = actual[str(fid)][key]
        e = m[key]
        if e is None:
            assert a is None, f'flight {fid} {key}: expected null, got {a}'
        else:
            assert a is not None, f'flight {fid} {key}: got null, expected {e}'
            assert abs(float(a) - e) <= tol, f'flight {fid} {key}: got {a}, expected {e}'


def test_output_exists():
    assert os.path.isfile(OUT)


def test_schema(actual, expected):
    assert isinstance(actual, dict)
    assert set(actual.keys()) == set(expected.keys())
    for fid in expected:
        assert set(actual[fid].keys()) == set(KEYS)


def test_rise_time(actual, expected):
    _check(actual, expected, 'RiseTime', 1e-3)


def test_settling_time(actual, expected):
    _check(actual, expected, 'SettlingTime', 1e-3)


def test_overshoot(actual, expected):
    _check(actual, expected, 'Overshoot_pct', 1e-3)


def test_steady_state_error(actual, expected):
    _check(actual, expected, 'SteadyStateError', 5e-4)

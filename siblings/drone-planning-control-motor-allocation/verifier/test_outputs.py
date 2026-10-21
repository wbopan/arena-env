import os

import numpy as np
import pandas as pd
import pytest
import yaml

WORK = '/root/work'
OUT = os.path.join(WORK, 'motor_output.csv')
COLS = ['id', 'rpm1', 'rpm2', 'rpm3', 'rpm4', 'F_act', 'Mx_act', 'My_act', 'Mz_act', 'saturated']


def compute_expected():
    with open(os.path.join(WORK, 'system_params.yaml')) as f:
        p = yaml.safe_load(f)
    cT = float(p['cT'])
    cQ = float(p['cQ'])
    d = float(p['arm_length'])
    lo = float(p['rpm_min'])
    hi = float(p['rpm_max'])
    A = np.array([[cT, cT, cT, cT],
                  [0.0, d * cT, 0.0, -d * cT],
                  [-d * cT, 0.0, d * cT, 0.0],
                  [-cQ, cQ, -cQ, cQ]])
    cmd = pd.read_csv(os.path.join(WORK, 'commands.csv')).sort_values('id')
    rows = []
    for _, r in cmd.iterrows():
        b = np.array([r['F'], r['Mx'], r['My'], r['Mz']], dtype=float)
        s = np.linalg.solve(A, b)
        raw = np.sqrt(np.maximum(s, 0.0))
        rpm = np.clip(raw, lo, hi)
        fm = A @ (rpm ** 2)
        sat = int(np.any(raw < lo) or np.any(raw > hi))
        rows.append([int(r['id'])] + list(rpm) + list(fm) + [sat])
    return pd.DataFrame(rows, columns=COLS)


@pytest.fixture(scope='module')
def expected():
    return compute_expected()


@pytest.fixture(scope='module')
def actual():
    assert os.path.isfile(OUT), 'missing motor_output.csv'
    return pd.read_csv(OUT)


def test_output_exists():
    assert os.path.isfile(OUT)


def test_header_and_ids(actual, expected):
    assert list(actual.columns) == COLS
    assert list(actual['id'].astype(int)) == list(expected['id'])


def test_rpm_values(actual, expected):
    for c in ['rpm1', 'rpm2', 'rpm3', 'rpm4']:
        diff = np.abs(actual[c].to_numpy(dtype=float) - expected[c].to_numpy(dtype=float))
        assert diff.max() <= 0.01, f'{c} max diff {diff.max()}'


def test_actual_force_moments(actual, expected):
    for c in ['F_act', 'Mx_act', 'My_act', 'Mz_act']:
        a = actual[c].to_numpy(dtype=float)
        e = expected[c].to_numpy(dtype=float)
        assert np.allclose(a, e, rtol=1e-6, atol=1e-5), f'{c} mismatch'


def test_saturation_flags(actual, expected):
    assert list(actual['saturated'].astype(int)) == list(expected['saturated'])

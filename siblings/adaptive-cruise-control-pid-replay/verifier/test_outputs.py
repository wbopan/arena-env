import os

import numpy as np
import pandas as pd
import pytest
import yaml

W = '/root/work'
OUT = os.path.join(W, 'commands.csv')
COLS = ['time', 'mode', 'accel_cmd', 'distance_error', 'ttc']


class PID:
    def __init__(self, kp, ki, kd):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.reset()

    def reset(self):
        self.i = 0.0
        self.prev = None

    def step(self, e, dt):
        self.i += e * dt
        der = 0.0 if self.prev is None else (e - self.prev) / dt
        self.prev = e
        return self.kp * e + self.ki * self.i + self.kd * der


def expected():
    with open(os.path.join(W, 'acc_config.yaml')) as f:
        cfg = yaml.safe_load(f)
    a, lim, g, dt = cfg['acc'], cfg['limits'], cfg['gains'], float(cfg['dt'])
    sp = PID(**g['pid_speed'])
    dp = PID(**g['pid_distance'])
    df = pd.read_csv(os.path.join(W, 'sensor_log.csv'))
    rows = []
    prev = None
    for r in df.itertuples(index=False):
        de = np.nan
        ttc = np.nan
        if pd.isna(r.lead_speed) or pd.isna(r.distance):
            mode = 'cruise'
        else:
            de = r.distance - (a['min_distance'] + a['time_headway'] * r.ego_speed)
            rel = r.ego_speed - r.lead_speed
            if rel > 0:
                ttc = r.distance / rel
            mode = 'emergency' if (not np.isnan(ttc) and ttc < a['ttc_threshold']) else 'follow'
        if mode != prev:
            sp.reset()
            dp.reset()
        if mode == 'cruise':
            u = sp.step(a['set_speed'] - r.ego_speed, dt)
        elif mode == 'follow':
            u = dp.step(de, dt)
        else:
            u = lim['max_decel']
        u = min(max(u, lim['max_decel']), lim['max_accel'])
        prev = mode
        rows.append([r.time, mode, u, de, ttc])
    return pd.DataFrame(rows, columns=COLS)


@pytest.fixture(scope='module')
def exp():
    return expected()


@pytest.fixture(scope='module')
def out():
    return pd.read_csv(OUT)


def test_output_exists():
    assert os.path.isfile(OUT)


def test_schema_and_rows(out, exp):
    assert list(out.columns) == COLS
    assert len(out) == len(exp)
    assert np.allclose(out['time'].astype(float).values, exp['time'].values, atol=1e-6)


def test_modes(out, exp):
    assert list(out['mode'].astype(str)) == list(exp['mode'])


def test_accel_cmd(out, exp):
    diff = np.abs(out['accel_cmd'].astype(float).values - exp['accel_cmd'].astype(float).values)
    assert diff.max() <= 1e-3, diff.max()


def test_distance_error_and_ttc(out, exp):
    for c in ['distance_error', 'ttc']:
        a = out[c].astype(float).values
        b = exp[c].astype(float).values
        assert np.array_equal(np.isnan(a), np.isnan(b)), c
        m = ~np.isnan(b)
        assert np.all(np.abs(a[m] - b[m]) <= 2e-3), c

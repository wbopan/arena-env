import json
import os
import numpy as np
import pandas as pd
import pytest
from scipy.optimize import curve_fit

WORK = '/root/work'
OUT = os.path.join(WORK, 'estimated_params.json')
KEYS = ['K', 'tau', 'y_ambient', 'r_squared', 'rmse', 'lambda', 'Kp', 'Ki']


def expected():
    df = pd.read_csv(os.path.join(WORK, 'calibration.csv'))
    on = df['heater_power'] > 0
    t0 = float(df['time'][on].iloc[0])
    u = float(df['heater_power'][on].iloc[0])
    ya = float(df['temperature'][df['time'] < t0].mean())
    sub = df[df['time'] >= t0]
    t = sub['time'].values - t0
    y = sub['temperature'].values

    def f(tt, K, tau):
        return ya + K * u * (1 - np.exp(-tt / tau))

    k0 = (y[-20:].mean() - ya) / u
    popt, _ = curve_fit(f, t, y, p0=[k0, 30.0], maxfev=20000)
    K, tau = float(popt[0]), float(popt[1])
    r = y - f(t, K, tau)
    r2 = 1 - np.sum(r ** 2) / np.sum((y - y.mean()) ** 2)
    rmse = float(np.sqrt(np.mean(r ** 2)))
    lam = 0.75 * tau
    Kp = tau / (K * lam)
    Ki = Kp / tau
    return {'K': K, 'tau': tau, 'y_ambient': ya, 'r_squared': float(r2), 'rmse': rmse, 'lambda': lam, 'Kp': Kp, 'Ki': Ki}


@pytest.fixture(scope='module')
def out():
    with open(OUT) as fh:
        return json.load(fh)


@pytest.fixture(scope='module')
def exp():
    return expected()


def test_file_exists():
    assert os.path.isfile(OUT)


def test_schema(out):
    for k in KEYS:
        assert k in out, k
        assert isinstance(out[k], (int, float)), k


def test_model_params(out, exp):
    assert abs(out['y_ambient'] - exp['y_ambient']) < 0.002
    assert out['K'] == pytest.approx(exp['K'], rel=0.01)
    assert out['tau'] == pytest.approx(exp['tau'], rel=0.02)


def test_fit_quality(out, exp):
    assert abs(out['r_squared'] - exp['r_squared']) < 0.005
    assert abs(out['rmse'] - exp['rmse']) < 0.003


def test_gains(out, exp):
    assert out['lambda'] == pytest.approx(exp['lambda'], rel=0.02)
    assert out['Kp'] == pytest.approx(exp['Kp'], rel=0.02)
    assert out['Ki'] == pytest.approx(exp['Ki'], rel=0.02)

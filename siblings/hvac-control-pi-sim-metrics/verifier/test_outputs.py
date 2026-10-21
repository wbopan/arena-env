import json
import math
import os
import pytest

WORK = '/root/work'
OUT = os.path.join(WORK, 'metrics.json')
KEYS = ['rise_time', 'settling_time', 'overshoot_pct', 'max_temp', 'steady_state_error', 'mean_heater_power', 'safety_cutoffs']


def expected():
    with open(os.path.join(WORK, 'params.json')) as fh:
        p = json.load(fh)
    dt = p['dt']
    n = int(round(p['duration'] / dt))
    T = [p['T0']]
    I = 0.0
    us = []
    cut = 0
    sp = p['setpoint']
    for k in range(n):
        e = sp - T[k]
        if T[k] >= p['T_max']:
            u = 0.0
            cut += 1
        else:
            ic = I + e * dt
            ur = p['Kp'] * e + p['Ki'] * ic
            u = min(100.0, max(0.0, ur))
            if 0.0 <= ur <= 100.0:
                I = ic
        us.append(u)
        T.append(T[k] + dt / p['tau'] * (p['T_ambient'] + p['K'] * u - T[k]))
    T0 = p['T0']
    thr = T0 + 0.9 * (sp - T0)
    rise = None
    for k, v in enumerate(T):
        if v >= thr:
            rise = k * dt
            break
    band = p['settle_band']
    last_out = None
    for k in range(len(T) - 1, -1, -1):
        if abs(T[k] - sp) > band:
            last_out = k
            break
    if last_out is None:
        settle = 0.0
    elif last_out == len(T) - 1:
        settle = None
    else:
        settle = (last_out + 1) * dt
    mx = max(T)
    m = max(1, int(math.floor(0.2 * (n + 1))))
    sse = abs(sum(T[-m:]) / m - sp)
    return {'rise_time': rise, 'settling_time': settle, 'overshoot_pct': max(0.0, (mx - sp) / (sp - T0)) * 100, 'max_temp': mx, 'steady_state_error': sse, 'mean_heater_power': sum(us) / n, 'safety_cutoffs': cut, 'dt': dt}


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


def test_timing(out, exp):
    for k in ['rise_time', 'settling_time']:
        if exp[k] is None:
            assert out[k] is None, k
        else:
            assert out[k] is not None, k
            assert abs(out[k] - exp[k]) <= exp['dt'] + 1e-9, k


def test_temperatures(out, exp):
    assert abs(out['max_temp'] - exp['max_temp']) < 0.01
    assert abs(out['overshoot_pct'] - exp['overshoot_pct']) < 0.2
    assert abs(out['steady_state_error'] - exp['steady_state_error']) < 0.01


def test_actuation(out, exp):
    assert abs(out['mean_heater_power'] - exp['mean_heater_power']) < 0.1
    assert abs(int(out['safety_cutoffs']) - exp['safety_cutoffs']) <= 1

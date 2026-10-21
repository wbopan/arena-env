import json
import os

import pandas as pd
import pytest
import yaml

W = '/root/work'
OUT = os.path.join(W, 'metrics.json')
KEYS = {'rise_time_s', 'overshoot_pct', 'speed_ss_error', 'distance_ss_error',
        'min_distance_m', 'min_ttc_s', 'follow_duration_s'}
TOL = 2e-3


def expected():
    with open(os.path.join(W, 'sim_config.yaml')) as f:
        cfg = yaml.safe_load(f)
    acc = cfg['acc_settings']
    s = float(acc['set_speed'])
    th = float(acc['time_headway'])
    md = float(acc['min_distance'])
    dt = float(cfg['simulation']['dt'])
    df = pd.read_csv(os.path.join(W, 'drive_log.csv'))
    lead = df['lead_speed'].notna()
    first = int(lead.to_numpy().argmax())
    cr = df.iloc[:first]
    t10 = cr.loc[cr['ego_speed'] >= 0.1 * s, 'time'].iloc[0]
    t90 = cr.loc[cr['ego_speed'] >= 0.9 * s, 'time'].iloc[0]
    ov = max(0.0, (cr['ego_speed'].max() - s) / s * 100.0)
    sse = abs(s - cr['ego_speed'].iloc[-25:].mean())
    tail = df.iloc[-50:]
    dse = abs((tail['distance'] - (md + th * tail['ego_speed'])).mean())
    ld = df[lead]
    rel = ld['ego_speed'] - ld['lead_speed']
    m = rel > 0
    ttc = float((ld['distance'][m] / rel[m]).min()) if m.any() else None
    return {
        'rise_time_s': float(t90 - t10),
        'overshoot_pct': float(ov),
        'speed_ss_error': float(sse),
        'distance_ss_error': float(dse),
        'min_distance_m': float(ld['distance'].min()),
        'min_ttc_s': ttc,
        'follow_duration_s': float(len(ld) * dt),
    }


@pytest.fixture(scope='module')
def exp():
    return expected()


@pytest.fixture(scope='module')
def out():
    with open(OUT) as f:
        return json.load(f)


def close(a, b):
    if b is None:
        return a is None
    return a is not None and abs(float(a) - b) <= TOL


def test_output_exists_and_is_json():
    assert os.path.isfile(OUT)
    with open(OUT) as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_keys(out):
    assert set(out.keys()) == KEYS


def test_speed_metrics(out, exp):
    for k in ['rise_time_s', 'overshoot_pct', 'speed_ss_error']:
        assert close(out[k], exp[k]), (k, out[k], exp[k])


def test_distance_metrics(out, exp):
    for k in ['distance_ss_error', 'min_distance_m']:
        assert close(out[k], exp[k]), (k, out[k], exp[k])


def test_ttc_and_duration(out, exp):
    for k in ['min_ttc_s', 'follow_duration_s']:
        assert close(out[k], exp[k]), (k, out[k], exp[k])

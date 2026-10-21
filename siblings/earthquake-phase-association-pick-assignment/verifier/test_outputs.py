import os
import numpy as np
import pandas as pd
import pytest

W = '/root/work'
OUT = os.path.join(W, 'assignments.csv')
VP = 6.0
VS = VP / 1.75
TOL = 1.0


def expected():
    st = pd.read_csv(os.path.join(W, 'stations.csv')).set_index('station_id')
    ev = pd.read_csv(os.path.join(W, 'events.csv'))
    pk = pd.read_csv(os.path.join(W, 'picks.csv'))
    ref = pd.Timestamp('2000-01-01')
    et = (pd.to_datetime(ev['time']) - ref).dt.total_seconds().to_numpy()
    pt = (pd.to_datetime(pk['timestamp']) - ref).dt.total_seconds().to_numpy()
    ex = ev['x_km'].to_numpy(float)
    ey = ev['y_km'].to_numpy(float)
    ez = ev['z_km'].to_numpy(float)
    res = {}
    for i in range(len(pk)):
        s = st.loc[pk['station_id'].iloc[i]]
        d = np.sqrt((ex - s['x_km']) ** 2 + (ey - s['y_km']) ** 2 + (ez + s['elevation_m'] / 1000.0) ** 2)
        v = VP if str(pk['phase'].iloc[i]).upper() == 'P' else VS
        r = np.abs(pt[i] - (et + d / v))
        j = int(np.argmin(r))
        res[str(pk['pick_id'].iloc[i])] = int(ev['event_id'].iloc[j]) if r[j] <= TOL else -1
    return res


@pytest.fixture(scope='module')
def out():
    assert os.path.exists(OUT), 'assignments.csv missing'
    return pd.read_csv(OUT)


def test_file_exists():
    assert os.path.exists(OUT)


def test_columns(out):
    assert list(out.columns)[:2] == ['pick_id', 'event_id']


def test_one_row_per_pick(out):
    exp = expected()
    got = out['pick_id'].astype(str).tolist()
    assert len(got) == len(set(got))
    assert set(got) == set(exp.keys())


def test_unassociated_set(out):
    exp = expected()
    got = dict(zip(out['pick_id'].astype(str), out['event_id'].astype(int)))
    exp_un = {k for k, v in exp.items() if v == -1}
    got_un = {k for k, v in got.items() if v == -1}
    assert exp_un == got_un


def test_all_assignments(out):
    exp = expected()
    got = dict(zip(out['pick_id'].astype(str), out['event_id'].astype(int)))
    wrong = [k for k in exp if got.get(k) != exp[k]]
    assert not wrong, f'{len(wrong)} wrong assignments, e.g. {wrong[:5]}'

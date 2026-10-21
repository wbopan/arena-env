import os
import numpy as np
import pandas as pd
import pytest
from scipy.optimize import least_squares

W = '/root/work'
OUT = os.path.join(W, 'locations.csv')
VP = 6.0
VS = VP / 1.75
DEPTH = 10.0
REF = pd.Timestamp('2000-01-01')


def expected():
    sta = pd.read_csv(os.path.join(W, 'stations.csv')).drop_duplicates(['network', 'station']).copy()
    lat0 = sta['latitude'].mean()
    lon0 = sta['longitude'].mean()
    sta['x'] = (sta['longitude'] - lon0) * 111.19 * np.cos(np.radians(lat0))
    sta['y'] = (sta['latitude'] - lat0) * 111.19
    sta['dz'] = DEPTH + sta['elevation_m'] / 1000.0
    sta.index = sta['network'].astype(str) + '.' + sta['station'].astype(str)
    pk = pd.read_csv(os.path.join(W, 'picks.csv'))
    pk['sid'] = pk['network'].astype(str) + '.' + pk['station'].astype(str)
    pk['t'] = (pd.to_datetime(pk['timestamp']) - REF).dt.total_seconds()
    res = {}
    for eid, g in pk.groupby('event_id'):
        sx = sta.loc[g['sid'], 'x'].to_numpy()
        sy = sta.loc[g['sid'], 'y'].to_numpy()
        dz = sta.loc[g['sid'], 'dz'].to_numpy()
        v = np.where(g['phase'].str.upper() == 'P', VP, VS)
        t = g['t'].to_numpy()
        tref = t.min()
        tr = t - tref

        def f(p):
            return p[2] + np.sqrt((p[0] - sx) ** 2 + (p[1] - sy) ** 2 + dz ** 2) / v - tr

        k = int(np.argmin(tr))
        sol = least_squares(f, [sx[k], sy[k], -2.0], xtol=1e-12, ftol=1e-12, gtol=1e-12)
        rms = float(np.sqrt(np.mean(f(sol.x) ** 2)))
        res[int(eid)] = (tref + sol.x[2], sol.x[0], sol.x[1], rms)
    return res


@pytest.fixture(scope='module')
def data():
    assert os.path.exists(OUT), 'locations.csv missing'
    out = pd.read_csv(OUT)
    return out, expected()


def test_file_exists():
    assert os.path.exists(OUT)


def test_schema(data):
    out, exp = data
    for c in ['event_id', 'time', 'x_km', 'y_km', 'rms_s']:
        assert c in out.columns, c
    ids = out['event_id'].astype(int).tolist()
    assert len(ids) == len(set(ids))
    assert set(ids) == set(exp.keys())


def test_origin_times(data):
    out, exp = data
    secs = (pd.to_datetime(out['time']) - REF).dt.total_seconds().to_numpy()
    for eid, s in zip(out['event_id'].astype(int), secs):
        assert abs(s - exp[eid][0]) < 0.05, f'event {eid}: time off by {s - exp[eid][0]:.3f} s'


def test_epicentres(data):
    out, exp = data
    for _, r in out.iterrows():
        e = exp[int(r['event_id'])]
        assert abs(r['x_km'] - e[1]) < 0.3 and abs(r['y_km'] - e[2]) < 0.3, f'event {r.event_id}'


def test_rms(data):
    out, exp = data
    for _, r in out.iterrows():
        e = exp[int(r['event_id'])]
        assert abs(r['rms_s'] - e[3]) < 0.005, f'event {r.event_id}: rms {r.rms_s} vs {e[3]:.4f}'

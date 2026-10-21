import json
import os

import numpy as np
import pandas as pd
import pytest

WORK = '/root/work'
OUT = os.path.join(WORK, 'boundary_summary.json')
R = 6371.0
TYPES = ['subduction', 'transform', 'ridge']


def poly_dist(P, Q):
    A = Q[:-1]
    D = Q[1:] - A
    L = (D ** 2).sum(axis=1)
    t = np.clip(((P - A) * D).sum(axis=1) / np.where(L == 0, 1.0, L), 0.0, 1.0)
    C = A + t[:, None] * D
    return float(np.sqrt(((P - C) ** 2).sum(axis=1)).min())


def compute_expected():
    with open(os.path.join(WORK, 'boundaries.geojson')) as fh:
        feats = json.load(fh)['features']
    lines = [(f['properties']['Type'], np.radians(np.array(f['geometry']['coordinates'], dtype=float)) * R) for f in feats]
    df = pd.read_csv(os.path.join(WORK, 'earthquakes.csv'))
    df = df[df['mag'] >= 4.5]
    groups = {t: [] for t in TYPES}
    unassoc = 0
    for _, r in df.iterrows():
        P = np.radians(np.array([r['longitude'], r['latitude']], dtype=float)) * R
        ds = [(poly_dist(P, Q), t) for t, Q in lines]
        d, t = min(ds, key=lambda x: x[0])
        if d <= 200.0:
            groups[t].append((d, float(r['mag'])))
        else:
            unassoc += 1
    return len(df), unassoc, groups


@pytest.fixture(scope='module')
def expected():
    return compute_expected()


@pytest.fixture(scope='module')
def out():
    assert os.path.exists(OUT), 'output JSON missing'
    with open(OUT) as fh:
        return json.load(fh)


def test_schema(out):
    assert 'n_events' in out and 'unassociated_count' in out and 'by_type' in out
    for t in TYPES:
        assert t in out['by_type'], t
        for k in ('count', 'mean_distance_km', 'max_magnitude'):
            assert k in out['by_type'][t], (t, k)


def test_n_events(out, expected):
    assert int(out['n_events']) == expected[0]


def test_counts(out, expected):
    assert int(out['unassociated_count']) == expected[1]
    for t in TYPES:
        assert int(out['by_type'][t]['count']) == len(expected[2][t]), t


def test_mean_distances(out, expected):
    for t in TYPES:
        v = expected[2][t]
        got = out['by_type'][t]['mean_distance_km']
        if not v:
            assert got is None
        else:
            exp = sum(d for d, _ in v) / len(v)
            assert got is not None and abs(float(got) - exp) <= 0.011, (t, got, exp)


def test_max_magnitude(out, expected):
    for t in TYPES:
        v = expected[2][t]
        got = out['by_type'][t]['max_magnitude']
        if not v:
            assert got is None
        else:
            assert got is not None and abs(float(got) - max(m for _, m in v)) <= 1e-6, t

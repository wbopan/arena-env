import csv
import json
import os

import numpy as np
import pytest
from matplotlib.path import Path

WORK = '/root/work'
OUT = os.path.join(WORK, 'plate_assignment.csv')
R = 6371.0
TOL = 0.011


def compute_expected():
    with open(os.path.join(WORK, 'plates.geojson')) as fh:
        plates = json.load(fh)['features']
    with open(os.path.join(WORK, 'earthquakes.geojson')) as fh:
        eqs = json.load(fh)['features']
    res = {}
    for f in eqs:
        lon, lat = f['geometry']['coordinates'][:2]
        for p in plates:
            ring = np.array(p['geometry']['coordinates'][0], dtype=float)
            if Path(ring).contains_point((lon, lat)):
                xy = np.radians(ring) * R
                P = np.radians(np.array([lon, lat], dtype=float)) * R
                A = xy[:-1]
                D = xy[1:] - A
                L = (D ** 2).sum(axis=1)
                t = np.clip(((P - A) * D).sum(axis=1) / np.where(L == 0, 1.0, L), 0.0, 1.0)
                C = A + t[:, None] * D
                d = float(np.sqrt(((P - C) ** 2).sum(axis=1)).min())
                res[str(f['properties']['id'])] = (p['properties']['Code'], d)
                break
    return res


@pytest.fixture(scope='module')
def expected():
    return compute_expected()


@pytest.fixture(scope='module')
def rows():
    assert os.path.exists(OUT), 'output CSV missing'
    with open(OUT, newline='') as fh:
        data = [r for r in csv.reader(fh) if r]
    return data


def test_file_exists():
    assert os.path.exists(OUT)


def test_header(rows):
    assert [c.strip() for c in rows[0]] == ['id', 'plate_code', 'distance_km']


def test_ids_match(rows, expected):
    ids = [r[0].strip() for r in rows[1:]]
    assert len(ids) == len(set(ids)), 'duplicate ids'
    assert set(ids) == set(expected.keys())


def test_plate_codes(rows, expected):
    for r in rows[1:]:
        eid = r[0].strip()
        assert eid in expected
        assert r[1].strip() == expected[eid][0], eid


def test_distances(rows, expected):
    for r in rows[1:]:
        eid = r[0].strip()
        assert abs(float(r[2]) - expected[eid][1]) <= TOL, (eid, r[2], expected[eid][1])


def test_sorted_descending(rows):
    d = [float(r[2]) for r in rows[1:]]
    assert all(d[i] >= d[i + 1] for i in range(len(d) - 1))

import json
import math
import os
from collections import defaultdict, deque

import pytest

W = '/root/work'
OUT = os.path.join(W, 'part_props.json')
KEYS = ['volume_cm3', 'centroid_mm', 'bbox_min_mm', 'bbox_max_mm', 'debris_count']


def expected():
    verts = []
    with open(os.path.join(W, 'part.stl')) as f:
        for line in f:
            t = line.split()
            if t and t[0] == 'vertex':
                verts.append(tuple(round(float(x), 4) for x in t[1:4]))
    tris = [tuple(verts[i:i + 3]) for i in range(0, len(verts), 3)]
    n = len(tris)
    vmap = defaultdict(list)
    for i, t in enumerate(tris):
        for p in t:
            vmap[p].append(i)
    seen = [False] * n
    comps = []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        q = deque([s])
        comp = []
        while q:
            i = q.popleft()
            comp.append(i)
            for p in tris[i]:
                for j in vmap[p]:
                    if not seen[j]:
                        seen[j] = True
                        q.append(j)
        comps.append(comp)
    best = None
    for comp in comps:
        dsum = 0.0
        m = [0.0, 0.0, 0.0]
        for i in comp:
            a, b, c = tris[i]
            cr = (b[1] * c[2] - b[2] * c[1], b[2] * c[0] - b[0] * c[2], b[0] * c[1] - b[1] * c[0])
            d = a[0] * cr[0] + a[1] * cr[1] + a[2] * cr[2]
            dsum += d
            for k in range(3):
                m[k] += d * (a[k] + b[k] + c[k]) / 4.0
        if best is None or abs(dsum) > abs(best[0]):
            best = (dsum, m, comp)
    dsum, m, comp = best
    pts = [p for i in comp for p in tris[i]]
    return {
        'volume_cm3': abs(dsum) / 6.0 / 1000.0,
        'centroid_mm': [m[k] / dsum for k in range(3)],
        'bbox_min_mm': [min(p[k] for p in pts) for k in range(3)],
        'bbox_max_mm': [max(p[k] for p in pts) for k in range(3)],
        'debris_count': len(comps) - 1,
    }


@pytest.fixture(scope='module')
def exp():
    return expected()


@pytest.fixture(scope='module')
def got():
    assert os.path.exists(OUT), 'part_props.json not found'
    with open(OUT) as f:
        return json.load(f)


def test_file_exists():
    assert os.path.exists(OUT)


def test_schema(got):
    for k in KEYS:
        assert k in got, f'missing key {k}'
    for k in ['centroid_mm', 'bbox_min_mm', 'bbox_max_mm']:
        assert isinstance(got[k], list) and len(got[k]) == 3
    assert isinstance(got['debris_count'], int)


def test_debris_count(got, exp):
    assert got['debris_count'] == exp['debris_count']


def test_volume(got, exp):
    assert math.isclose(float(got['volume_cm3']), exp['volume_cm3'], rel_tol=1e-3)


def test_centroid(got, exp):
    for g, e in zip(got['centroid_mm'], exp['centroid_mm']):
        assert abs(float(g) - e) <= 0.01, f'centroid {got["centroid_mm"]} vs {exp["centroid_mm"]}'


def test_bbox(got, exp):
    for key in ['bbox_min_mm', 'bbox_max_mm']:
        for g, e in zip(got[key], exp[key]):
            assert abs(float(g) - e) <= 0.002, f'{key}: {got[key]} vs {exp[key]}'

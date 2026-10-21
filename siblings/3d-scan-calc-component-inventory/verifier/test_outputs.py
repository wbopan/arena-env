import csv
import math
import os
import struct
from collections import defaultdict, deque

import pytest

W = '/root/work'
OUT = os.path.join(W, 'components.csv')
COLS = ['rank', 'material_id', 'triangles', 'volume_mm3', 'area_mm2', 'mass_g']


def load_density():
    d = {}
    with open(os.path.join(W, 'materials.md')) as f:
        for line in f:
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) >= 3 and cells[0].isdigit():
                d[int(cells[0])] = float(cells[2])
    return d


def sub(p, q):
    return (p[0] - q[0], p[1] - q[1], p[2] - q[2])


def cross(p, q):
    return (p[1] * q[2] - p[2] * q[1], p[2] * q[0] - p[0] * q[2], p[0] * q[1] - p[1] * q[0])


def expected_rows():
    with open(os.path.join(W, 'build_plate.stl'), 'rb') as f:
        data = f.read()
    n = struct.unpack_from('<I', data, 80)[0]
    tris = []
    for i in range(n):
        v = struct.unpack_from('<12fH', data, 84 + 50 * i)
        tris.append((v[3:6], v[6:9], v[9:12], v[12]))
    vmap = defaultdict(list)
    for i, t in enumerate(tris):
        for p in t[:3]:
            vmap[p].append(i)
    seen = [False] * n
    dens = load_density()
    rows = []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        q = deque([s])
        comp = []
        while q:
            i = q.popleft()
            comp.append(i)
            for p in tris[i][:3]:
                for j in vmap[p]:
                    if not seen[j]:
                        seen[j] = True
                        q.append(j)
        vol = 0.0
        area = 0.0
        for i in comp:
            a, b, c = tris[i][:3]
            cr = cross(b, c)
            vol += a[0] * cr[0] + a[1] * cr[1] + a[2] * cr[2]
            k = cross(sub(b, a), sub(c, a))
            area += 0.5 * math.sqrt(k[0] ** 2 + k[1] ** 2 + k[2] ** 2)
        vol = abs(vol) / 6.0
        mid = tris[comp[0]][3]
        rows.append({'material_id': mid, 'triangles': len(comp), 'volume_mm3': vol,
                     'area_mm2': area, 'mass_g': vol / 1000.0 * dens[mid]})
    rows.sort(key=lambda r: -r['volume_mm3'])
    return rows


@pytest.fixture(scope='module')
def exp():
    return expected_rows()


@pytest.fixture(scope='module')
def got():
    assert os.path.exists(OUT), 'components.csv not found'
    with open(OUT, newline='') as f:
        rows = [r for r in csv.reader(f) if r]
    return rows


def data_rows(got):
    return [dict(zip([h.strip() for h in got[0]], [c.strip() for c in r])) for r in got[1:]]


def test_file_exists():
    assert os.path.exists(OUT)


def test_header(got):
    assert [h.strip() for h in got[0]] == COLS


def test_row_count_and_ranks(got, exp):
    rows = data_rows(got)
    assert len(rows) == len(exp), f'expected {len(exp)} components, got {len(rows)}'
    assert [int(float(r['rank'])) for r in rows] == list(range(1, len(exp) + 1))


def test_ids_and_triangle_counts(got, exp):
    rows = data_rows(got)
    assert len(rows) == len(exp)
    for r, e in zip(rows, exp):
        assert int(float(r['material_id'])) == e['material_id']
        assert int(float(r['triangles'])) == e['triangles']


def test_volume_and_area(got, exp):
    rows = data_rows(got)
    assert len(rows) == len(exp)
    for r, e in zip(rows, exp):
        assert math.isclose(float(r['volume_mm3']), e['volume_mm3'], rel_tol=1e-3, abs_tol=2e-3)
        assert math.isclose(float(r['area_mm2']), e['area_mm2'], rel_tol=1e-3, abs_tol=2e-3)


def test_mass(got, exp):
    rows = data_rows(got)
    assert len(rows) == len(exp)
    for r, e in zip(rows, exp):
        assert math.isclose(float(r['mass_g']), e['mass_g'], rel_tol=1e-3, abs_tol=2e-4)

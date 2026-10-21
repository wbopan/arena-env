import csv
import json
from pathlib import Path

import pytest

W = Path('/root/work')
OUT = W / 'route_leaks.csv'
HEADER = ['path_id', 'prefix', 'leaker_as', 'source_as', 'destination_as', 'source_type', 'destination_type']
INV = {'customer': 'provider', 'provider': 'customer', 'peer': 'peer'}
BAD = {'provider', 'peer'}


def expected_rows():
    rel = {}
    with open(W / 'relationships.csv', newline='') as f:
        rd = csv.reader(f)
        next(rd)
        for r in rd:
            if not r:
                continue
            a, b, t = int(r[0]), int(r[1]), r[2].strip()
            rel[(a, b)] = t
            rel[(b, a)] = INV[t]
    props = json.loads((W / 'propagations.json').read_text())
    props.sort(key=lambda p: p['path_id'])
    rows = []
    for p in props:
        ap = p['as_path']
        for i in range(1, len(ap) - 1):
            src, lk, dst = ap[i - 1], ap[i], ap[i + 1]
            st = rel[(lk, src)]
            dt = rel[(lk, dst)]
            if st in BAD and dt in BAD:
                rows.append([str(p['path_id']), p['prefix'], str(lk), str(src), str(dst), st, dt])
    return rows


@pytest.fixture(scope='module')
def got():
    assert OUT.exists(), 'route_leaks.csv missing'
    with open(OUT, newline='') as f:
        rows = [[c.strip() for c in r] for r in csv.reader(f) if r]
    return rows


@pytest.fixture(scope='module')
def exp():
    return expected_rows()


def test_header(got):
    assert got[0] == HEADER


def test_row_count(got, exp):
    assert len(got) - 1 == len(exp)


def test_leak_set(got, exp):
    assert sorted(map(tuple, got[1:])) == sorted(map(tuple, exp))


def test_types_valid(got):
    for r in got[1:]:
        assert r[5] in BAD and r[6] in BAD


def test_exact_order(got, exp):
    assert got[1:] == exp

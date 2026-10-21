import csv
import math
from collections import defaultdict
from pathlib import Path

import pytest

IN = Path('/root/work/traffic.csv')
OUT = Path('/root/work/beacon_report.csv')
HEADER = ['src_ip', 'dst_ip', 'packets', 'total_bytes', 'iat_mean', 'iat_cv', 'is_beacon']


def expected():
    g = defaultdict(list)
    with IN.open(newline='') as f:
        for r in csv.DictReader(f):
            if not r['src_ip'].strip() or not r['dst_ip'].strip():
                continue
            g[(r['src_ip'], r['dst_ip'])].append((float(r['ts']), int(r['length'])))
    res = {}
    for k, v in g.items():
        if len(v) < 10:
            continue
        ts = sorted(t for t, _ in v)
        iats = [b - a for a, b in zip(ts, ts[1:])]
        m = sum(iats) / len(iats)
        var = sum((x - m) ** 2 for x in iats) / len(iats)
        cv = math.sqrt(var) / m if m > 0 else 0.0
        res[k] = {'packets': len(v), 'total_bytes': sum(l for _, l in v),
                  'iat_mean': m, 'iat_cv': cv, 'is_beacon': cv < 0.5}
    return res


@pytest.fixture(scope='module')
def exp():
    return expected()


@pytest.fixture(scope='module')
def got():
    assert OUT.exists(), 'beacon_report.csv missing'
    with OUT.open(newline='') as f:
        rows = [r for r in csv.reader(f) if r]
    assert rows, 'empty file'
    return rows


def body(rows):
    return {(r[0].strip(), r[1].strip()): r for r in rows[1:]}


def test_header(got):
    assert [c.strip() for c in got[0]] == HEADER


def test_pairs_and_order(got, exp):
    keys = [(r[0].strip(), r[1].strip()) for r in got[1:]]
    assert keys == sorted(exp.keys())


def test_counts_and_bytes(got, exp):
    b = body(got)
    for k, e in exp.items():
        assert k in b, k
        assert int(b[k][2]) == e['packets'], k
        assert int(float(b[k][3])) == e['total_bytes'], k


def test_iat_stats(got, exp):
    b = body(got)
    for k, e in exp.items():
        assert abs(float(b[k][4]) - e['iat_mean']) <= 0.002, k
        assert abs(float(b[k][5]) - e['iat_cv']) <= 0.001, k


def test_beacon_flags(got, exp):
    b = body(got)
    for k, e in exp.items():
        assert b[k][6].strip() == ('true' if e['is_beacon'] else 'false'), k

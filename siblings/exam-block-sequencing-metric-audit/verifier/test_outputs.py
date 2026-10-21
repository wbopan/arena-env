import csv
import json
from pathlib import Path

import pytest

W = Path('/root/work')
OUT = W / 'metrics.json'
KEYS = ['objective', 'eve_morn_b2b_count', 'other_b2b_count',
        'same_day_triple_count', 'cross_day_triple_count', 'z_three_in_four_count']


def _expected():
    inst = json.loads((W / 'instance.json').read_text())
    pair = {}
    with open(W / 'pair_counts.csv', newline='') as f:
        for r in csv.DictReader(f):
            pair[(r['block_i'], r['block_j'])] = int(r['count'])
    trip = {}
    with open(W / 'triplet_counts.csv', newline='') as f:
        for r in csv.DictReader(f):
            trip[(r['block_i'], r['block_j'], r['block_k'])] = int(r['count'])
    at = {}
    with open(W / 'schedule.csv', newline='') as f:
        for r in csv.DictReader(f):
            at[r['slot']] = r['block']
    order = inst['slot_order']
    pos = {s: i for i, s in enumerate(order)}

    def b(s, k):
        return at[order[pos[s] + k]]

    em = sum(pair.get((b(s, 0), b(s, 1)), 0) for s in inst['eve_morn_start'])
    ot = sum(pair.get((b(s, 0), b(s, 1)), 0) for s in inst['other_b2b_start'])
    sd = sum(trip.get((b(s, 0), b(s, 1), b(s, 2)), 0) for s in inst['triple_day_start'])
    cd = sum(trip.get((b(s, 0), b(s, 1), b(s, 2)), 0) for s in inst['triple_24_start'])
    z = sum(trip.get((b(s, 0), b(s, 1), b(s, 3)), 0) + trip.get((b(s, 0), b(s, 2), b(s, 3)), 0)
            for s in inst['four_start'])
    return {
        'objective': em + ot + 10 * sd + 10 * cd + 5 * z,
        'eve_morn_b2b_count': em,
        'other_b2b_count': ot,
        'same_day_triple_count': sd,
        'cross_day_triple_count': cd,
        'z_three_in_four_count': z,
    }


@pytest.fixture(scope='module')
def got():
    assert OUT.exists(), 'metrics.json missing'
    return json.loads(OUT.read_text())


@pytest.fixture(scope='module')
def exp():
    return _expected()


def test_file_exists():
    assert OUT.exists()


def test_schema(got):
    for k in KEYS:
        assert k in got, f'missing key {k}'
        v = got[k]
        assert isinstance(v, (int, float)) and float(v) == int(v), f'{k} not integer'


def test_b2b_counts(got, exp):
    assert int(got['eve_morn_b2b_count']) == exp['eve_morn_b2b_count']
    assert int(got['other_b2b_count']) == exp['other_b2b_count']


def test_triple_counts(got, exp):
    assert int(got['same_day_triple_count']) == exp['same_day_triple_count']
    assert int(got['cross_day_triple_count']) == exp['cross_day_triple_count']


def test_three_in_four(got, exp):
    assert int(got['z_three_in_four_count']) == exp['z_three_in_four_count']


def test_objective(got, exp):
    assert int(got['objective']) == exp['objective']

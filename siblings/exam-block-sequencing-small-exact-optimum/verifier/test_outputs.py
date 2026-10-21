import csv
import itertools
import json
from pathlib import Path

import pytest

W = Path('/root/work')
OUT = W / 'schedule.csv'


def _load():
    inst = json.loads((W / 'instance.json').read_text())
    pair = {}
    with open(W / 'pair_counts.csv', newline='') as f:
        for r in csv.DictReader(f):
            pair[(r['block_i'], r['block_j'])] = int(r['count'])
    trip = {}
    with open(W / 'triplet_counts.csv', newline='') as f:
        for r in csv.DictReader(f):
            trip[(r['block_i'], r['block_j'], r['block_k'])] = int(r['count'])
    return inst, pair, trip


def _objective(seq, inst, pair, trip):
    pos = {s: i for i, s in enumerate(inst['slot_order'])}
    wb = inst['weights']['b2b']
    wt = inst['weights']['triple']
    v = 0
    for s in inst['b2b_start']:
        i = pos[s]
        v += wb * pair.get((seq[i], seq[i + 1]), 0)
    for s in inst['triple_start']:
        i = pos[s]
        v += wt * trip.get((seq[i], seq[i + 1], seq[i + 2]), 0)
    return v


def _optimum(inst, pair, trip):
    pos = {s: i for i, s in enumerate(inst['slot_order'])}
    early = {pos[s] for s in inst['early_slots']}
    large = set(inst['large_blocks'])
    best = None
    for p in itertools.permutations(inst['blocks']):
        if any(p[i] in large and i not in early for i in range(len(p))):
            continue
        v = _objective(p, inst, pair, trip)
        if best is None or v < best:
            best = v
    return best


@pytest.fixture(scope='module')
def data():
    return _load()


@pytest.fixture(scope='module')
def rows():
    assert OUT.exists(), 'schedule.csv missing'
    with open(OUT, newline='') as f:
        rd = csv.DictReader(f)
        assert rd.fieldnames is not None
        assert [h.strip() for h in rd.fieldnames] == ['slot', 'block']
        return [{k.strip(): (v or '').strip() for k, v in r.items()} for r in rd]


def test_file_and_header(rows):
    assert len(rows) > 0


def test_one_row_per_slot(rows, data):
    inst = data[0]
    slots = [r['slot'] for r in rows]
    assert len(slots) == len(inst['slot_order'])
    assert sorted(slots) == sorted(inst['slot_order'])


def test_blocks_permutation(rows, data):
    inst = data[0]
    assert sorted(r['block'] for r in rows) == sorted(inst['blocks'])


def test_front_loading(rows, data):
    inst = data[0]
    at = {r['slot']: r['block'] for r in rows}
    early_blocks = {at[s] for s in inst['early_slots']}
    for b in inst['large_blocks']:
        assert b in early_blocks, f'large block {b} not in an early slot'


def test_optimal_objective(rows, data):
    inst, pair, trip = data
    at = {r['slot']: r['block'] for r in rows}
    seq = [at[s] for s in inst['slot_order']]
    got = _objective(seq, inst, pair, trip)
    best = _optimum(inst, pair, trip)
    assert got == best, f'objective {got} != optimum {best}'

import csv
import itertools
import json
from collections import Counter
from pathlib import Path

ROOT = Path('/root/work')


def expected():
    d = json.loads((ROOT / 'instance.json').read_text())
    with (ROOT / 'pair_counts.csv').open(newline='') as f:
        pair = {(r['first'], r['second']): int(r['count']) for r in csv.DictReader(f)}
    with (ROOT / 'triple_counts.csv').open(newline='') as f:
        triple = {(r['first'], r['second'], r['third']): int(r['count']) for r in csv.DictReader(f)}
    counts = Counter()
    for p in itertools.permutations(d['blocks']):
        if not all(d['slot_order'][p.index(b)] in d['early_slots'] for b in d['large_blocks']):
            continue
        a = sum(pair[p[i], p[i + 1]] for i in range(len(p) - 1))
        b = sum(triple[p[i], p[i + 1], p[i + 2]] for i in range(len(p) - 2))
        counts[a, b] += 1
    return [{'pair_cost': a, 'triple_cost': b, 'multiplicity': counts[a, b]} for a, b in sorted(counts) if not any((x <= a and y <= b and (x < a or y < b)) for x, y in counts)]


def output():
    return json.loads((ROOT / 'frontier.json').read_text())


def test_file_exists():
    assert (ROOT / 'frontier.json').is_file()


def test_schema_and_types():
    d = output()
    assert set(d) == {'frontier'}
    assert isinstance(d['frontier'], list) and d['frontier']
    for row in d['frontier']:
        assert set(row) == {'pair_cost', 'triple_cost', 'multiplicity'}
        assert all(type(row[k]) is int for k in row)
        assert row['multiplicity'] > 0


def test_pairs_and_order():
    observed = output()['frontier']
    reference = expected()
    assert [(r['pair_cost'], r['triple_cost']) for r in observed] == [(r['pair_cost'], r['triple_cost']) for r in reference]


def test_multiplicities():
    assert [r['multiplicity'] for r in output()['frontier']] == [r['multiplicity'] for r in expected()]

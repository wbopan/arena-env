import csv
import itertools
import json
from pathlib import Path

ROOT = Path('/root/work')


def data():
    spec = json.loads((ROOT / 'instance.json').read_text())
    with (ROOT / 'pair_counts.csv').open(newline='') as f:
        pair = {(r['first'], r['second']): int(r['count']) for r in csv.DictReader(f)}
    with (ROOT / 'triple_counts.csv').open(newline='') as f:
        triple = {(r['first'], r['second'], r['third']): int(r['count']) for r in csv.DictReader(f)}
    return spec, pair, triple


def rows():
    with (ROOT / 'schedule.csv').open(newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def test_file_exists():
    assert (ROOT / 'schedule.csv').is_file()


def test_schema_and_slot_order():
    spec, _, _ = data()
    columns, schedule = rows()
    assert columns == ['slot', 'block']
    assert [r['slot'] for r in schedule] == spec['slot_order']


def test_permutation_and_early_rule():
    spec, _, _ = data()
    _, schedule = rows()
    names = [r['block'] for r in schedule]
    assert sorted(names) == sorted(spec['blocks'])
    assert all(schedule[i]['slot'] in spec['early_slots'] for i, name in enumerate(names) if name in spec['large_blocks'])


def test_exact_optimum_and_tiebreak():
    spec, pair, triple = data()
    names = tuple(r['block'] for r in rows()[1])
    def cost(p):
        return sum(pair[p[i], p[i + 1]] for i in spec['pair_starts']) + 3 * sum(triple[p[i], p[i + 1], p[i + 2]] for i in spec['triple_starts'])
    eligible = ((cost(p), p) for p in itertools.permutations(spec['blocks']) if all(spec['slot_order'][p.index(b)] in spec['early_slots'] for b in spec['large_blocks']))
    assert (cost(names), names) == min(eligible)

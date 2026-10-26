import csv
import itertools
import json
from pathlib import Path

ROOT = Path('/root/work')


def read(name):
    with (ROOT / name).open(newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def inputs():
    spec = json.loads((ROOT / 'instance.json').read_text())
    _, missing_rows = read('missing_pairs.csv')
    missing = [(r['first'], r['second']) for r in missing_rows]
    _, known_rows = read('pair_counts.csv')
    known = {(r['first'], r['second']): int(r['count']) for r in known_rows}
    _, observations = read('observations.csv')
    return spec, missing, known, observations


def test_file_exists():
    assert (ROOT / 'inferred_pairs.csv').is_file()


def test_schema_and_order():
    _, missing, _, _ = inputs()
    header, result = read('inferred_pairs.csv')
    assert header == ['first', 'second', 'count']
    assert [(r['first'], r['second']) for r in result] == missing


def test_counts_are_integers_in_range():
    _, result = read('inferred_pairs.csv')
    assert all(r['count'] in [str(n) for n in range(1, 7)] for r in result)


def test_recovered_counts_match_unique_solution():
    spec, missing, known, observations = inputs()
    equations = []
    for row in observations:
        p = [row[s] for s in spec['slot_order']]
        edges = list(zip(p, p[1:]))
        coefficients = [edges.count(key) for key in missing]
        residual = int(row['total']) - sum(known[e] for e in edges if e in known)
        equations.append((coefficients, residual))
    solutions = [x for x in itertools.product(range(1, 7), repeat=len(missing)) if all(sum(a * b for a, b in zip(coef, x)) == rhs for coef, rhs in equations)]
    assert len(solutions) == 1
    _, result = read('inferred_pairs.csv')
    assert tuple(int(r['count']) for r in result) == solutions[0]

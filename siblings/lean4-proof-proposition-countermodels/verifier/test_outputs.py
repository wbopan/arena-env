import itertools
import json
from pathlib import Path

ROOT = Path('/root/work')
VARS = 'abcd'


def truth(formula, assignment):
    if 'var' in formula:
        return assignment[formula['var']]
    if 'not' in formula:
        return not truth(formula['not'], assignment)
    for name in ('and', 'or', 'imp'):
        if name in formula:
            left, right = (truth(x, assignment) for x in formula[name])
            if name == 'and':
                return left and right
            if name == 'or':
                return left or right
            return not left or right
    raise ValueError(formula)


def expected():
    answers = []
    for claim in json.loads((ROOT / 'claims.json').read_text()):
        witness = None
        for bits in itertools.product((False, True), repeat=4):
            assignment = dict(zip(VARS, bits))
            if not truth(claim['formula'], assignment):
                witness = assignment
                break
        answers.append({'id': claim['id'], 'valid': witness is None,
                        'counterexample': witness})
    return answers


def output():
    return json.loads((ROOT / 'countermodels.json').read_text())


def test_file_exists():
    assert (ROOT / 'countermodels.json').is_file()


def test_schema():
    rows = output()
    assert isinstance(rows, list) and len(rows) == len(expected())
    for row in rows:
        assert isinstance(row, dict) and set(row) == {'id', 'valid', 'counterexample'}
        assert isinstance(row['id'], str) and type(row['valid']) is bool
        witness = row['counterexample']
        assert witness is None or (isinstance(witness, dict) and set(witness) == set(VARS)
            and all(type(value) is bool for value in witness.values()))


def test_ids_and_validity():
    assert [(r['id'], r['valid']) for r in output()] == [(r['id'], r['valid']) for r in expected()]


def test_first_counterexamples():
    assert [r['counterexample'] for r in output()] == [r['counterexample'] for r in expected()]

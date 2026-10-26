import json
import math
from pathlib import Path
from openpyxl import load_workbook

ROOT = Path('/root/work')
OUT = ROOT / 'coexpression_pairs.json'

def expected():
    wb = load_workbook(ROOT / 'coexpression_panel.xlsx', data_only=True)
    table = list(wb['Data'].values)
    profiles = {row[0]: [float(v) for v in row[1:]] for row in table[1:]}
    answer = []
    for pair_id, a, b in list(wb['Pairs'].values)[1:]:
        x, y = profiles[a], profiles[b]
        xbar, ybar = sum(x) / len(x), sum(y) / len(y)
        numerator = sum((u - xbar) * (v - ybar) for u, v in zip(x, y))
        denominator = math.sqrt(sum((u - xbar) ** 2 for u in x) * sum((v - ybar) ** 2 for v in y))
        answer.append((pair_id, a, b, numerator / denominator))
    return sorted(answer, key=lambda row: (-abs(row[3]), row[0]))

def result():
    return json.loads(OUT.read_text())

def test_file_exists():
    assert OUT.is_file()

def test_schema_and_pair_coverage():
    obj = result()
    assert set(obj) == {'pairs', 'strongest_pair_id'}
    assert isinstance(obj['pairs'], list)
    assert all(set(row) == {'pair_id', 'protein_a', 'protein_b', 'pearson_r'} for row in obj['pairs'])
    assert {(r['pair_id'], r['protein_a'], r['protein_b']) for r in obj['pairs']} == {(i, a, b) for i, a, b, _ in expected()}
    assert len(obj['pairs']) == len(expected())

def test_pearson_coefficients():
    actual = {r['pair_id']: r['pearson_r'] for r in result()['pairs']}
    for pair_id, _, _, coefficient in expected():
        value = actual[pair_id]
        assert type(value) in (int, float) and not isinstance(value, bool)
        assert math.isclose(value, coefficient, abs_tol=0.000051)

def test_ranking():
    assert [r['pair_id'] for r in result()['pairs']] == [row[0] for row in expected()]

def test_strongest_pair():
    obj = result()
    assert obj['strongest_pair_id'] == expected()[0][0]

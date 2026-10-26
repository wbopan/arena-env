import json
from pathlib import Path

P = Path('/root/work')

def cube(p):
    x, y = p
    q = x - (y - y % 2) // 2
    return q, -q-y, y

def distance(a, b):
    return sum(abs(i-j) for i, j in zip(cube(a), cube(b))) // 2

def expected():
    data = json.loads((P/'settlement.json').read_text())
    results = []
    for c in data['candidates']:
        worked = [t for t in data['tiles'] if distance(c, (t['x'], t['y'])) <= 2]
        results.append((sum(t['weight'] for t in worked), len(worked), c))
    value, count, center = min(results, key=lambda r: (-r[0], r[2][1], r[2][0]))
    return {'center': center, 'value': value, 'worked_count': count}

def answer():
    return json.loads((P/'settlement_answer.json').read_text())

def test_file_exists():
    assert (P/'settlement_answer.json').is_file()

def test_schema():
    a = answer()
    assert set(a) == {'center', 'value', 'worked_count'}
    assert isinstance(a['center'], list) and len(a['center']) == 2
    assert all(type(v) is int for v in a['center'])
    assert type(a['value']) is int and type(a['worked_count']) is int

def test_optimal_center():
    assert answer()['center'] == expected()['center']

def test_coverage_values():
    a, e = answer(), expected()
    assert (a['value'], a['worked_count']) == (e['value'], e['worked_count'])

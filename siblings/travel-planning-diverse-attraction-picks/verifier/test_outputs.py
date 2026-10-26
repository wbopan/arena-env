import csv
import itertools
import json
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'sights.json'


def inputs():
    visit = json.loads((ROOT / 'visit.json').read_text())
    with (ROOT / 'attractions.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    return visit, rows


def optimal():
    visit, rows = inputs()
    groups = [[r for r in rows if r['City'] == city] for city in visit['cities']]
    feasible = []
    for choice in itertools.product(*groups):
        cost = sum(int(r['AdmissionUSD']) for r in choice)
        if cost <= visit['budget_usd'] and len({r['Category'] for r in choice}) == len(choice):
            score = sum(int(r['Score']) for r in choice)
            feasible.append(((-score, cost, tuple(r['Name'] for r in choice)), choice))
    choice = min(feasible, key=lambda pair: pair[0])[1]
    return [{'city': r['City'], 'attraction': r['Name'], 'category': r['Category'], 'admission_usd': int(r['AdmissionUSD']), 'score': int(r['Score'])} for r in choice]


def test_file_exists():
    assert OUT.is_file()


def test_schema():
    data = json.loads(OUT.read_text())
    cities = inputs()[0]['cities']
    assert set(data) == {'selected', 'total_admission_usd', 'total_score'}
    assert isinstance(data['selected'], list) and len(data['selected']) == len(cities)
    assert [r['city'] for r in data['selected']] == cities
    assert all(set(r) == {'city', 'attraction', 'category', 'admission_usd', 'score'} for r in data['selected'])
    assert all(type(r[k]) is int for r in data['selected'] for k in ('admission_usd', 'score'))
    assert type(data['total_admission_usd']) is int and type(data['total_score']) is int


def test_feasibility_and_source_records():
    data = json.loads(OUT.read_text())
    visit, rows = inputs()
    original = {(r['City'], r['Name'], r['Category'], int(r['AdmissionUSD']), int(r['Score'])) for r in rows}
    assert all((r['city'], r['attraction'], r['category'], r['admission_usd'], r['score']) in original for r in data['selected'])
    assert len({r['category'] for r in data['selected']}) == len(visit['cities'])
    assert sum(r['admission_usd'] for r in data['selected']) <= visit['budget_usd']


def test_optimum_and_totals():
    data = json.loads(OUT.read_text())
    assert data['selected'] == optimal()
    assert data['total_admission_usd'] == sum(r['admission_usd'] for r in data['selected'])
    assert data['total_score'] == sum(r['score'] for r in data['selected'])

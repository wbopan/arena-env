import csv
import json
from pathlib import Path

ROOT = Path('/root/work')

def reference():
    groups = json.loads((ROOT / 'requests.json').read_text())
    original = json.loads((ROOT / 'candidate_routes.json').read_text())['routes']
    with (ROOT / 't_matrix.csv').open() as f:
        matrix = [list(map(int, row)) for row in csv.reader(f)]
    ids = ['DEP'] + [node for group in groups for trip in group['trips'] for node in (trip['pickup_node'], trip['dropoff_node'])]
    complete = []
    keep = set()
    for group in groups:
        valid = True
        for trip in group['trips']:
            p, d = trip['pickup_node'], trip['dropoff_node']
            occurrences_p = [(v, pos) for v, route in enumerate(original) for pos, node in enumerate(route) if node == p]
            occurrences_d = [(v, pos) for v, route in enumerate(original) for pos, node in enumerate(route) if node == d]
            valid &= len(occurrences_p) == len(occurrences_d) == 1 and occurrences_p[0][0] == occurrences_d[0][0] and occurrences_p[0][1] < occurrences_d[0][1] if occurrences_p and occurrences_d else False
        if valid:
            complete.append(group['group_id'])
            for trip in group['trips']:
                keep.update((trip['pickup_node'], trip['dropoff_node']))
    cleaned = [[node for node in route if node == 'DEP' or node in keep] for route in original]
    total = sum(matrix[ids.index(a)][ids.index(b)] for route in cleaned for a, b in zip(route, route[1:]))
    return sorted(complete), cleaned, total

def output():
    return json.loads((ROOT / 'cleaned_plan.json').read_text())

def test_file_exists():
    assert (ROOT / 'cleaned_plan.json').is_file()

def test_schema():
    data = output()
    assert set(data) == {'complete_group_ids', 'cleaned_routes', 'total_travel_min'}
    assert isinstance(data['complete_group_ids'], list)
    assert isinstance(data['cleaned_routes'], list)
    assert type(data['total_travel_min']) is int

def test_completed_groups():
    assert output()['complete_group_ids'] == reference()[0]

def test_cleaned_route_sequences():
    assert output()['cleaned_routes'] == reference()[1]

def test_recomputed_travel():
    assert output()['total_travel_min'] == reference()[2]

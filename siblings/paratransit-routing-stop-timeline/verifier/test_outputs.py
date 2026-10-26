import csv
import json
from pathlib import Path

ROOT = Path('/root/work')
COLUMNS = ['node', 'arrival_min', 'start_min', 'depart_min', 'wait_min', 'load_after']

def expected():
    trips = json.loads((ROOT / 'requests.json').read_text())
    route = json.loads((ROOT / 'route.json').read_text())
    matrix = [[int(x) for x in row] for row in csv.reader((ROOT / 't_matrix.csv').open())]
    ids = ['DEP'] + [n for r in trips for n in (r['pickup_node'], r['dropoff_node'])]
    t = route['start_min']
    load = 0
    result = [['DEP', t, t, t, 0, 0]]
    for previous, node in zip(route['node_sequence'], route['node_sequence'][1:]):
        arrival = t + matrix[ids.index(previous)][ids.index(node)]
        if node == 'DEP':
            start, duration = arrival, 0
        else:
            r = next(r for r in trips if node in (r['pickup_node'], r['dropoff_node']))
            kind = 'pickup' if node == r['pickup_node'] else 'dropoff'
            low, high = r[kind + '_tw']
            start = max(arrival, low)
            assert start <= high
            duration = r['service_min'][kind]
            load += r['load'] if kind == 'pickup' else -r['load']
            assert 0 <= load <= 4
        t = start + duration
        result.append([node, arrival, start, t, start-arrival, load])
    return result

def rows():
    with (ROOT / 'timeline.csv').open(newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == COLUMNS
        return list(reader)

def test_file_exists():
    assert (ROOT / 'timeline.csv').is_file()

def test_row_schema_and_order():
    actual = rows()
    target = expected()
    assert len(actual) == len(target)
    assert [r['node'] for r in actual] == [r[0] for r in target]
    for row in actual:
        assert all(row[k].lstrip('-').isdigit() for k in COLUMNS[1:])

def test_times_and_waiting():
    for actual, target in zip(rows(), expected()):
        assert [int(actual[k]) for k in COLUMNS[1:5]] == target[1:5]

def test_passenger_loads():
    assert [int(r['load_after']) for r in rows()] == [r[5] for r in expected()]

import csv
import json
from pathlib import Path

ROOT = Path('/root/work')

def reference():
    trips = json.loads((ROOT / 'requests.json').read_text())
    base = json.loads((ROOT / 'base_route.json').read_text())
    with (ROOT / 't_matrix.csv').open() as f:
        matrix = [list(map(int, row)) for row in csv.reader(f)]
    nodes = ['DEP'] + [n for trip in trips for n in (trip['pickup_node'], trip['dropoff_node'])]
    def distance(seq):
        return sum(matrix[nodes.index(a)][nodes.index(b)] for a, b in zip(seq, seq[1:]))
    def starts(seq):
        minute, load, result = base['start_min'], 0, []
        for old, node in zip(seq, seq[1:]):
            minute += matrix[nodes.index(old)][nodes.index(node)]
            if node == 'DEP':
                return result if minute <= base['end_limit_min'] and load == 0 else None
            trip = next(t for t in trips if node in (t['pickup_node'], t['dropoff_node']))
            kind = 'pickup' if node == trip['pickup_node'] else 'dropoff'
            minute = max(minute, trip[kind + '_tw'][0])
            if minute > trip[kind + '_tw'][1]:
                return None
            result.append(minute)
            load += trip['load'] if kind == 'pickup' else -trip['load']
            if not 0 <= load <= base['capacity']:
                return None
            minute += trip[kind + '_service_min']
        return None
    original = base['node_sequence'][1:-1]
    choices = []
    for p in range(6):
        for d in range(p+1, 6):
            stops = original.copy()
            stops.insert(p, trips[2]['pickup_node'])
            stops.insert(d, trips[2]['dropoff_node'])
            sequence = ['DEP'] + stops + ['DEP']
            times = starts(sequence)
            if times is not None:
                choices.append((distance(sequence)-distance(base['node_sequence']), p, d, times))
    assert choices
    return min(choices, key=lambda x: x[:3])

def output():
    return json.loads((ROOT / 'insertion.json').read_text())

def test_file_exists():
    assert (ROOT / 'insertion.json').is_file()

def test_schema():
    data = output()
    assert set(data) == {'pickup_index', 'dropoff_index', 'added_travel_min', 'service_starts_min'}
    assert all(type(data[k]) is int for k in ('pickup_index', 'dropoff_index', 'added_travel_min'))
    assert isinstance(data['service_starts_min'], list)
    assert len(data['service_starts_min']) == 6
    assert all(type(t) is int for t in data['service_starts_min'])

def test_optimal_positions_and_cost():
    cost, p, d, _ = reference()
    data = output()
    assert (data['added_travel_min'], data['pickup_index'], data['dropoff_index']) == (cost, p, d)

def test_service_start_times():
    assert output()['service_starts_min'] == reference()[3]

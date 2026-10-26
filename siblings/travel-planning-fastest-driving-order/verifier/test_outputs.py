import csv
import itertools
import json
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'route.json'


def expected():
    trip = json.loads((ROOT / 'trip.json').read_text())
    ohio = {city for state, city in (line.strip().split('\t') for line in (ROOT / 'cities.txt').read_text().splitlines()) if state == 'Ohio'}
    assert set([trip['start'], trip['end'], *trip['stops']]) <= ohio
    edges = {}
    with (ROOT / 'distance.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            h, m = row['duration'].split(' hours ')
            edges[row['origin'], row['destination']] = (int(h) * 60 + int(m.split()[0]), int(row['distance'].split()[0]))
    candidates = []
    for stops in itertools.permutations(trip['stops']):
        route = [trip['start'], *stops, trip['end']]
        pairs = list(zip(route, route[1:]))
        minutes = sum(edges[p][0] for p in pairs)
        km = sum(edges[p][1] for p in pairs)
        candidates.append(((minutes, km, stops), route, pairs))
    _, route, pairs = min(candidates)
    legs = [{'origin': a, 'destination': b, 'distance_km': edges[a, b][1], 'duration_min': edges[a, b][0]} for a, b in pairs]
    return route, legs


def test_file_exists():
    assert OUT.is_file()


def test_schema():
    data = json.loads(OUT.read_text())
    assert set(data) == {'ordered_city_names', 'legs', 'total_distance_km', 'total_duration_min'}
    assert isinstance(data['ordered_city_names'], list) and isinstance(data['legs'], list)
    assert len(data['legs']) == len(data['ordered_city_names']) - 1
    assert all(set(leg) == {'origin', 'destination', 'distance_km', 'duration_min'} for leg in data['legs'])
    assert all(type(leg[k]) is int for leg in data['legs'] for k in ('distance_km', 'duration_min'))
    assert type(data['total_distance_km']) is int and type(data['total_duration_min']) is int


def test_optimal_order_and_legs():
    data = json.loads(OUT.read_text())
    route, legs = expected()
    assert data['ordered_city_names'] == route
    assert data['legs'] == legs


def test_totals():
    data = json.loads(OUT.read_text())
    assert data['total_distance_km'] == sum(x['distance_km'] for x in data['legs'])
    assert data['total_duration_min'] == sum(x['duration_min'] for x in data['legs'])

import csv
import json
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'association.json'


def reference():
    with (ROOT / 'stations.csv').open(newline='') as f:
        stations = {r['station']: int(r['distance_km']) for r in csv.DictReader(f)}
    options = {}
    with (ROOT / 'candidates.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            options.setdefault((r['station'], r['phase']), []).append(int(r['pick_idx']))
    results = []
    for origin in range(61):
        chosen = []
        cost = 0
        for station in sorted(stations):
            for phase, speed in [('P', 6), ('S', 3)]:
                arrival = origin + stations[station] * 10 // speed
                pick = min(options[(station, phase)], key=lambda x: (abs(x - arrival), x))
                cost += abs(pick - arrival)
                chosen.append({'station': station, 'phase': phase, 'pick_idx': pick})
        results.append((cost, origin, chosen))
    return min(results, key=lambda x: (x[0], x[1]))


def output():
    return json.loads(OUT.read_text())


def test_file_exists():
    assert OUT.is_file()


def test_schema():
    obj = output()
    assert set(obj) == {'origin_idx', 'total_residual_samples', 'picks'}
    assert type(obj['origin_idx']) is int
    assert type(obj['total_residual_samples']) is int
    assert isinstance(obj['picks'], list)
    assert all(set(p) == {'station', 'phase', 'pick_idx'} and isinstance(p['station'], str) and p['phase'] in ('P', 'S') and type(p['pick_idx']) is int for p in obj['picks'])


def test_origin_and_residual():
    cost, origin, _ = reference()
    obj = output()
    assert obj['origin_idx'] == origin
    assert obj['total_residual_samples'] == cost


def test_associated_picks():
    assert output()['picks'] == reference()[2]

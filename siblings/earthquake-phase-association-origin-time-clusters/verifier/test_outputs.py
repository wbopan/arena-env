import csv
import math
from pathlib import Path

BASE = Path('/root/work')

def expected():
    with (BASE / 'stations.csv').open() as f:
        stations = {r['station_id']: (float(r['x_km']), float(r['y_km'])) for r in csv.DictReader(f)}
    estimates = []
    with (BASE / 'picks.csv').open() as f:
        for r in csv.DictReader(f):
            if float(r['prob']) < 0.8:
                continue
            x, y = stations[r['station_id']]
            distance = math.dist((x, y, 0), (9, 0, 6))
            estimates.append((float(r['time_s']) - distance / (6 if r['phase'] == 'p' else 3), r['station_id'], r['phase']))
    estimates.sort()
    groups = []
    for item in estimates:
        if not groups or item[0] - groups[-1][-1][0] > 0.30:
            groups.append([])
        groups[-1].append(item)
    return [(sum(v[0] for v in g) / len(g), len(g), len({v[1] for v in g})) for g in groups if len({v[1] for v in g}) >= 3 and sum(v[2] == 'p' for v in g) >= 2]

def actual():
    with (BASE / 'events.csv').open() as f:
        return list(csv.DictReader(f))

def test_file_exists():
    assert (BASE / 'events.csv').is_file()

def test_schema():
    with (BASE / 'events.csv').open() as f:
        assert next(csv.reader(f)) == ['time_s', 'n_picks', 'n_stations']

def test_event_count_and_order():
    rows = actual()
    assert len(rows) == len(expected())
    assert [float(r['time_s']) for r in rows] == sorted(float(r['time_s']) for r in rows)

def test_origin_times():
    for row, (time, _, _) in zip(actual(), expected()):
        assert abs(float(row['time_s']) - time) <= 0.00051

def test_counts():
    for row, (_, picks, stations) in zip(actual(), expected()):
        assert int(row['n_picks']) == picks
        assert int(row['n_stations']) == stations

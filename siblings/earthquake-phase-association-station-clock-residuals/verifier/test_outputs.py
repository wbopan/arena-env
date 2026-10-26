import csv
import json
import math
import statistics
from pathlib import Path

BASE = Path('/root/work')

def expected():
    def read(name):
        with (BASE / name).open() as f:
            return list(csv.DictReader(f))
    sites = {r['station_id']: (float(r['x_km']), float(r['y_km'])) for r in read('stations.csv')}
    events = read('events.csv')
    selected = {}
    for pick in read('picks.csv'):
        probability = float(pick['prob'])
        if probability < .8:
            continue
        sid = pick['station_id']
        x, y = sites[sid]
        observed = float(pick['time_s'])
        candidates = []
        for e in events:
            distance = math.sqrt((x-float(e['x_km']))**2 + (y-float(e['y_km']))**2 + float(e['depth_km'])**2)
            residual = observed - float(e['time_s']) - distance/6
            candidates.append((abs(residual), e['event_id'], residual))
        absolute, eid, residual = min(candidates)
        if absolute > 2:
            continue
        key = (sid, eid)
        rank = (-probability, observed)
        if key not in selected or rank < selected[key][0]:
            selected[key] = (rank, residual)
    result = {}
    for sid in sites:
        values = [value[1] for (station, _), value in selected.items() if station == sid]
        result[sid] = (statistics.median(values) if values else None, len(values))
    return result

def actual():
    return json.loads((BASE / 'clock_offsets.json').read_text())

def test_file_exists():
    assert (BASE / 'clock_offsets.json').is_file()

def test_schema_and_order():
    rows = actual()
    assert isinstance(rows, list)
    assert all(set(row) == {'station_id', 'offset_s', 'count'} for row in rows)
    assert [r['station_id'] for r in rows] == sorted(expected())

def test_counts():
    assert all(isinstance(r['count'], int) and r['count'] == expected()[r['station_id']][1] for r in actual())

def test_offsets():
    for row in actual():
        offset = expected()[row['station_id']][0]
        if offset is None:
            assert row['offset_s'] is None
        else:
            assert isinstance(row['offset_s'], (int, float))
            assert abs(row['offset_s'] - offset) <= .00051

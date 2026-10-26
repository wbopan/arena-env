import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'action_lead_times.tsv'
COLUMNS = ['station_id', 'first_action_date', 'first_flood_date', 'lead_days']


def expected():
    with (ROOT / 'nws_gauges.csv').open(newline='') as f:
        thresholds = {r[0]: (float(r[1]), float(r[2])) for r in list(csv.reader(f))[1:]}
    with (ROOT / 'gage_height_iv.rdb').open() as f:
        lines = [s.rstrip('\n') for s in f if not s.startswith('#')]
    names = lines[0].split('\t')
    readings = defaultdict(list)
    for line in lines[2:]:
        row = dict(zip(names, line.split('\t')))
        if row['site_no'] in thresholds and row['00065']:
            readings[(row['site_no'], row['datetime'][:10])].append(float(row['00065']))
    result = []
    for sid in sorted(thresholds):
        daily = sorted((day, max(values)) for (station, day), values in readings.items() if station == sid)
        action = next((day for day, peak in daily if peak >= thresholds[sid][0]), None)
        flood = next((day for day, peak in daily if peak >= thresholds[sid][1]), None)
        if flood is not None:
            assert action is not None
            result.append({'station_id': sid, 'first_action_date': action, 'first_flood_date': flood, 'lead_days': str((date.fromisoformat(flood) - date.fromisoformat(action)).days)})
    return result


def output():
    with OUT.open(newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        return reader.fieldnames, list(reader)


def test_exists():
    assert OUT.is_file()


def test_schema():
    fields, rows = output()
    assert fields == COLUMNS
    assert all(set(r) == set(COLUMNS) and all(r.values()) for r in rows)


def test_included_stations_and_dates():
    _, rows = output()
    want = expected()
    assert [(r['station_id'], r['first_action_date'], r['first_flood_date']) for r in rows] == [(r['station_id'], r['first_action_date'], r['first_flood_date']) for r in want]


def test_lead_days():
    _, rows = output()
    assert [r['lead_days'] for r in rows] == [r['lead_days'] for r in expected()]

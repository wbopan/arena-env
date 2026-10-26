import csv
import json
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'flood_events.json'
KEYS = {'station_id', 'start_date', 'end_date', 'duration_days', 'peak_ft'}


def expected():
    with (ROOT / 'nws_gauges.csv').open(newline='') as f:
        rows = list(csv.reader(f))[1:]
    thresholds = {row[0]: float(row[1]) for row in rows}
    with (ROOT / 'gage_height_iv.rdb').open() as f:
        content = [line.rstrip('\n') for line in f if not line.startswith('#')]
    columns = content[0].split('\t')
    daily = defaultdict(list)
    for line in content[2:]:
        r = dict(zip(columns, line.split('\t')))
        if r['00065'] and r['site_no'] in thresholds:
            daily[(r['site_no'], date.fromisoformat(r['datetime'][:10]))].append(float(r['00065']))
    result = []
    for sid in sorted(thresholds):
        active = None
        for n in range(1, 11):
            day = date(2025, 6, 1) + timedelta(days=n - 1)
            heights = daily.get((sid, day), []) if n <= 9 else []
            flooded = bool(heights) and max(heights) >= thresholds[sid]
            if flooded:
                if active is None:
                    active = {'station_id': sid, 'start_date': day.isoformat(), 'end_date': day.isoformat(), 'duration_days': 0, 'peak_ft': float('-inf')}
                active['end_date'] = day.isoformat()
                active['duration_days'] += 1
                active['peak_ft'] = max(active['peak_ft'], max(heights))
            elif active is not None:
                active['peak_ft'] = round(active['peak_ft'], 2)
                result.append(active)
                active = None
    return result


def load():
    return json.loads(OUT.read_text())


def test_exists():
    assert OUT.is_file()


def test_schema():
    data = load()
    assert isinstance(data, list)
    assert all(isinstance(r, dict) and set(r) == KEYS for r in data)
    assert all(isinstance(r['station_id'], str) and isinstance(r['duration_days'], int) and not isinstance(r['duration_days'], bool) and isinstance(r['peak_ft'], (float, int)) for r in data)


def test_event_boundaries_and_order():
    data, target = load(), expected()
    assert [(r['station_id'], r['start_date'], r['end_date'], r['duration_days']) for r in data] == [(r['station_id'], r['start_date'], r['end_date'], r['duration_days']) for r in target]


def test_peak_heights():
    data, target = load(), expected()
    assert len(data) == len(target)
    assert all(abs(a['peak_ft'] - b['peak_ft']) <= 0.005 for a, b in zip(data, target))

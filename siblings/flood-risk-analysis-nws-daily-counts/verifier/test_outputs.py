import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'flood_day_counts.csv'


def expected():
    with (ROOT / 'nws_gauges.csv').open(newline='') as f:
        rows = list(csv.reader(f))
    limits = {r[0]: float(r[1]) for r in rows[1:] if float(r[1]) != -9999}
    peaks = defaultdict(list)
    with (ROOT / 'gage_height_iv.rdb').open() as f:
        lines = [line for line in f if not line.startswith('#')]
    columns = lines[0].rstrip('\n').split('\t')
    for line in lines[2:]:
        record = dict(zip(columns, line.rstrip('\n').split('\t')))
        if record['site_no'] in limits and record['00065']:
            peaks[(record['site_no'], record['datetime'][:10])].append(float(record['00065']))
    counts = defaultdict(int)
    for (sid, _), values in peaks.items():
        if max(values) >= limits[sid]:
            counts[sid] += 1
    return [{'station_id': sid, 'flood_days': str(counts[sid])} for sid in sorted(counts)]


def read_output():
    with OUT.open(newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def test_exists():
    assert OUT.is_file()


def test_schema():
    columns, rows = read_output()
    assert columns == ['station_id', 'flood_days']
    assert all(set(row) == set(columns) and all(row.values()) for row in rows)


def test_stations_and_order():
    _, rows = read_output()
    assert [r['station_id'] for r in rows] == [r['station_id'] for r in expected()]


def test_flood_counts():
    _, rows = read_output()
    assert rows == expected()

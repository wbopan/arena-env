import csv
import json
import math
from collections import Counter
from pathlib import Path

SOURCE = Path('/root/work/traffic.csv')
OUTPUT = Path('/root/work/minute_profile.json')
TOP_KEYS = {'total_packets', 'occupied_minutes', 'average_ppm', 'peak_ppm', 'has_dos_pattern', 'buckets'}
BUCKET_KEYS = {'minute_index', 'packet_count', 'share_percent'}


def truth():
    with SOURCE.open(newline='') as f:
        timestamps = [float(r['ts']) for r in csv.DictReader(f)]
    start = min(timestamps)
    counts = Counter(math.floor((t-start)/60) for t in timestamps)
    n = len(timestamps)
    avg = n / len(counts)
    return n, counts, avg


def output():
    return json.loads(OUTPUT.read_text())


def test_exists():
    assert OUTPUT.is_file()


def test_schema():
    doc = output()
    assert set(doc) == TOP_KEYS
    assert isinstance(doc['has_dos_pattern'], bool)
    assert isinstance(doc['buckets'], list)
    assert all(isinstance(b, dict) and set(b) == BUCKET_KEYS for b in doc['buckets'])


def test_buckets():
    doc = output()
    n, counts, _ = truth()
    assert [b['minute_index'] for b in doc['buckets']] == sorted(counts)
    for b in doc['buckets']:
        count = counts[b['minute_index']]
        assert type(b['packet_count']) is int and b['packet_count'] == count
        assert math.isclose(b['share_percent'], round(100*count/n, 3), abs_tol=0.000001)


def test_rates_and_detection():
    doc = output()
    n, counts, avg = truth()
    assert doc['total_packets'] == n
    assert doc['occupied_minutes'] == len(counts)
    assert math.isclose(doc['average_ppm'], round(avg, 3), abs_tol=0.000001)
    assert doc['peak_ppm'] == max(counts.values())
    assert doc['has_dos_pattern'] is (max(counts.values()) / avg > 20)

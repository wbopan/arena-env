import csv
import ipaddress
import json
from collections import defaultdict
from pathlib import Path

INPUT = Path('/root/work/eve.json')
OUTPUT = Path('/root/work/source_totals.csv')
FIELDS = ['src_ip', 'transactions', 'body_bytes']


def expected():
    http = {}
    alerted = set()
    for line in INPUT.read_text().splitlines():
        event = json.loads(line)
        key = (event.get('flow_id'), event.get('tx_id'))
        if event['event_type'] == 'http':
            http[key] = event
        elif event['event_type'] == 'alert' and event['alert']['signature_id'] == 1000001:
            alerted.add(key)
    totals = defaultdict(lambda: [0, 0])
    for key in alerted & http.keys():
        event = http[key]
        h = event['http']
        if (h['http_method'], h['url'], h['x_tlm_mode']) == ('POST', '/telemetry/v2/report', 'exfil'):
            totals[event['src_ip']][0] += 1
            totals[event['src_ip']][1] += h['request_body_len']
    return [[ip, str(totals[ip][0]), str(totals[ip][1])]
            for ip in sorted(totals, key=ipaddress.ip_address)]


def read_csv():
    with OUTPUT.open(newline='') as f:
        return list(csv.reader(f))


def test_file_exists():
    assert OUTPUT.is_file()


def test_header_and_shape():
    rows = read_csv()
    assert rows[0] == FIELDS
    assert all(len(row) == 3 for row in rows[1:])
    assert all(all(value.isdecimal() for value in row[1:]) for row in rows[1:])


def test_sources_and_order():
    assert [row[0] for row in read_csv()[1:]] == [row[0] for row in expected()]


def test_transaction_counts():
    assert [row[1] for row in read_csv()[1:]] == [row[1] for row in expected()]


def test_body_byte_sums():
    assert [row[2] for row in read_csv()[1:]] == [row[2] for row in expected()]

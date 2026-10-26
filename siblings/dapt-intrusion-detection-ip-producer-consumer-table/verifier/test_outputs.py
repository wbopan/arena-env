import csv
from collections import defaultdict
from pathlib import Path

SOURCE = Path('/root/work/traffic.csv')
OUTPUT = Path('/root/work/ip_roles.csv')
HEADER = ['ip', 'bytes_sent', 'bytes_recv', 'pcr', 'outdegree', 'indegree', 'role']


def expected():
    sent, recv = defaultdict(int), defaultdict(int)
    outgoing, incoming = defaultdict(set), defaultdict(set)
    with SOURCE.open(newline='') as f:
        for row in csv.DictReader(f):
            a, b = row['src_ip'], row['dst_ip']
            if not a or not b:
                continue
            size = int(row['length'])
            sent[a] += size
            recv[b] += size
            outgoing[a].add(b)
            incoming[b].add(a)
    result = {}
    for ip in sent.keys() | recv.keys():
        s, r = sent[ip], recv[ip]
        ratio = (s-r)/(s+r)
        role = 'producer' if ratio > .2 else 'consumer' if ratio < -.2 else 'balanced'
        result[ip] = (s, r, ratio, len(outgoing[ip]), len(incoming[ip]), role)
    return result


def read_output():
    with OUTPUT.open(newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def test_exists():
    assert OUTPUT.is_file()


def test_schema_and_order():
    header, rows = read_output()
    assert header == HEADER
    assert [r['ip'] for r in rows] == sorted(expected())


def test_byte_totals_and_degrees():
    _, rows = read_output()
    for row in rows:
        s, r, _, out, inc, _ = expected()[row['ip']]
        assert (int(row['bytes_sent']), int(row['bytes_recv'])) == (s, r)
        assert (int(row['outdegree']), int(row['indegree'])) == (out, inc)


def test_pcr_and_roles():
    _, rows = read_output()
    truth = expected()
    for row in rows:
        ratio, role = truth[row['ip']][2], truth[row['ip']][5]
        assert row['pcr'] == f'{ratio:.6f}'
        assert row['role'] == role

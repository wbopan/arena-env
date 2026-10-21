import json
import math
import struct
from collections import Counter, defaultdict
from pathlib import Path

import pytest

PCAP = Path('/root/work/capture.pcap')
OUT = Path('/root/work/scan_report.json')


def ip_key(s):
    return tuple(int(x) for x in s.split('.'))


def expected():
    data = PCAP.read_bytes()
    magic = struct.unpack('<I', data[:4])[0]
    e = '<' if magic == 0xA1B2C3D4 else '>'
    off = 24
    ports = defaultdict(Counter)
    syn = Counter()
    tot = Counter()
    while off + 16 <= len(data):
        _, _, incl, _ = struct.unpack(e + 'IIII', data[off:off + 16])
        off += 16
        fr = data[off:off + incl]
        off += incl
        if len(fr) < 34 or struct.unpack('!H', fr[12:14])[0] != 0x0800:
            continue
        if fr[23] != 6:
            continue
        t = 14 + (fr[14] & 15) * 4
        if len(fr) < t + 14:
            continue
        src = '.'.join(str(b) for b in fr[26:30])
        dport = struct.unpack('!H', fr[t + 2:t + 4])[0]
        fl = fr[t + 13]
        ports[src][dport] += 1
        tot[src] += 1
        if (fl & 2) and not (fl & 16):
            syn[src] += 1
    rows = []
    for src in sorted(tot, key=ip_key):
        n = tot[src]
        if n < 30:
            continue
        c = ports[src]
        h = -sum(v / n * math.log2(v / n) for v in c.values())
        r = syn[src] / n
        rows.append({'src_ip': src, 'tcp_packets': n, 'unique_dst_ports': len(c),
                     'port_entropy': h, 'syn_only_ratio': r,
                     'is_scanner': (h > 5.0 and r > 0.7 and len(c) > 40)})
    return rows


@pytest.fixture(scope='module')
def exp():
    return expected()


@pytest.fixture(scope='module')
def got():
    assert OUT.exists(), 'scan_report.json missing'
    return json.loads(OUT.read_text())


def test_schema(got):
    assert isinstance(got, dict)
    assert isinstance(got.get('sources'), list)
    assert isinstance(got.get('scanners'), list)
    for s in got['sources']:
        for k in ('src_ip', 'tcp_packets', 'unique_dst_ports', 'port_entropy', 'syn_only_ratio', 'is_scanner'):
            assert k in s, k
        assert isinstance(s['is_scanner'], bool)


def test_sources_and_order(got, exp):
    assert [s['src_ip'] for s in got['sources']] == [e['src_ip'] for e in exp]


def test_counts(got, exp):
    for g, e in zip(got['sources'], exp):
        assert int(g['tcp_packets']) == e['tcp_packets'], e['src_ip']
        assert int(g['unique_dst_ports']) == e['unique_dst_ports'], e['src_ip']


def test_entropy_and_ratio(got, exp):
    for g, e in zip(got['sources'], exp):
        assert abs(float(g['port_entropy']) - e['port_entropy']) <= 1e-3, e['src_ip']
        assert abs(float(g['syn_only_ratio']) - e['syn_only_ratio']) <= 1e-3, e['src_ip']


def test_scanner_flags(got, exp):
    for g, e in zip(got['sources'], exp):
        assert g['is_scanner'] == e['is_scanner'], e['src_ip']
    assert got['scanners'] == [e['src_ip'] for e in exp if e['is_scanner']]

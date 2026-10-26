import csv
import ipaddress
import struct
from collections import defaultdict
from pathlib import Path

PCAP = Path('/root/work/capture.pcap')
OUTPUT = Path('/root/work/flows.tsv')
HEADER = ['proto', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'packet_count', 'total_bytes', 'has_reverse']


def expected():
    raw = PCAP.read_bytes()
    assert raw[:4] == b'\xd4\xc3\xb2\xa1'
    assert struct.unpack_from('<I', raw, 20)[0] == 1
    result = defaultdict(lambda: [0, 0])
    offset = 24
    while offset < len(raw):
        _, _, size, _ = struct.unpack_from('<IIII', raw, offset)
        offset += 16
        ethernet = raw[offset:offset+size]
        offset += size
        if ethernet[12:14] != b'\x08\x00':
            continue
        ip = ethernet[14:]
        if ip[0] >> 4 != 4 or ip[9] not in (6, 17):
            continue
        transport = ip[(ip[0] & 15)*4:]
        sport, dport = struct.unpack_from('!HH', transport)
        key = ('TCP' if ip[9] == 6 else 'UDP', str(ipaddress.IPv4Address(ip[12:16])),
               str(ipaddress.IPv4Address(ip[16:20])), sport, dport)
        result[key][0] += 1
        result[key][1] += size
    assert offset == len(raw)
    return result


def rows():
    with OUTPUT.open(newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        return reader.fieldnames, list(reader)


def key(row):
    return (row['proto'], row['src_ip'], row['dst_ip'], int(row['src_port']), int(row['dst_port']))


def test_exists():
    assert OUTPUT.is_file()


def test_schema_and_flow_keys():
    header, data = rows()
    assert header == HEADER
    assert [key(r) for r in data] == sorted(expected())


def test_counts_and_bytes():
    for row in rows()[1]:
        assert (int(row['packet_count']), int(row['total_bytes'])) == tuple(expected()[key(row)])


def test_reverse_flags():
    flows = expected()
    for row in rows()[1]:
        proto, src, dst, sport, dport = key(row)
        reverse = (proto, dst, src, dport, sport)
        assert row['has_reverse'] == ('true' if reverse in flows else 'false')

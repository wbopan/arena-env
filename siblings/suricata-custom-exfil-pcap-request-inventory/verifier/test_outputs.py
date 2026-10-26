import hashlib
import ipaddress
import json
import struct
from collections import defaultdict
from pathlib import Path

PCAP = Path('/root/work/telemetry.pcap')
OUTPUT = Path('/root/work/request_inventory.json')
FIELDS = {'src_ip', 'src_port', 'method', 'uri', 'body_bytes', 'body_sha256'}


def expected():
    data = PCAP.read_bytes()
    assert struct.unpack_from('<I', data)[0] == 0xa1b2c3d4
    offset = 24
    parts = defaultdict(dict)
    while offset < len(data):
        _, _, length, _ = struct.unpack_from('<IIII', data, offset)
        frame = data[offset + 16:offset + 16 + length]
        offset += 16 + length
        ihl = (frame[14] & 15) * 4
        ip = frame[14:]
        source = str(ipaddress.IPv4Address(ip[12:16]))
        tcp = ip[ihl:]
        sport, dport, seq = struct.unpack_from('!HHI', tcp)
        tcp_header_len = (tcp[12] >> 4) * 4
        payload = tcp[tcp_header_len:]
        if dport == 80 and payload:
            parts[(source, sport)][seq] = payload
    result = []
    for (source, sport), segments in parts.items():
        wire = b''.join(segments[seq] for seq in sorted(segments))
        headers, remainder = wire.split(b'\r\n\r\n', 1)
        lines = headers.split(b'\r\n')
        method, uri, _ = lines[0].decode('ascii').split(' ', 2)
        length = int(next(line.split(b':', 1)[1].strip() for line in lines[1:]
                          if line.lower().startswith(b'content-length:')))
        body = remainder[:length]
        result.append({'src_ip': source, 'src_port': sport, 'method': method,
                       'uri': uri, 'body_bytes': len(body),
                       'body_sha256': hashlib.sha256(body).hexdigest()})
    return sorted(result, key=lambda row: row['src_port'])


def actual():
    return json.loads(OUTPUT.read_text())


def test_file_exists():
    assert OUTPUT.is_file()


def test_schema():
    rows = actual()
    assert isinstance(rows, list)
    assert all(set(row) == FIELDS for row in rows)
    assert all(type(r['src_port']) is int and type(r['body_bytes']) is int for r in rows)
    assert all(isinstance(r[k], str) for r in rows for k in ('src_ip', 'method', 'uri', 'body_sha256'))


def test_request_identity_and_order():
    keys = ('src_ip', 'src_port', 'method', 'uri')
    assert [tuple(row[k] for k in keys) for row in actual()] == [tuple(row[k] for k in keys) for row in expected()]


def test_body_lengths():
    assert [row['body_bytes'] for row in actual()] == [row['body_bytes'] for row in expected()]


def test_body_hashes():
    assert [row['body_sha256'] for row in actual()] == [row['body_sha256'] for row in expected()]

#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_flow_ledger.py <<'PY'
import csv
import ipaddress
import struct
from collections import defaultdict

raw = open('/root/work/capture.pcap', 'rb').read()
flows = defaultdict(lambda: [0, 0])
pos = 24
while pos < len(raw):
    sec, usec, captured, original = struct.unpack_from('<IIII', raw, pos)
    pos += 16
    packet = raw[pos:pos+captured]
    pos += captured
    if packet[12:14] != b'\x08\x00':
        continue
    ip = packet[14:]
    if ip[0] >> 4 != 4 or ip[9] not in (6, 17):
        continue
    ports_at = (ip[0] & 15) * 4
    src_port, dst_port = struct.unpack_from('!HH', ip, ports_at)
    src = str(ipaddress.IPv4Address(ip[12:16]))
    dst = str(ipaddress.IPv4Address(ip[16:20]))
    proto = 'TCP' if ip[9] == 6 else 'UDP'
    stats = flows[(proto, src, dst, src_port, dst_port)]
    stats[0] += 1
    stats[1] += captured
with open('/root/work/flows.tsv', 'w', newline='') as f:
    w = csv.writer(f, delimiter='\t')
    w.writerow(['proto', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'packet_count', 'total_bytes', 'has_reverse'])
    for key in sorted(flows):
        proto, src, dst, sport, dport = key
        reverse = (proto, dst, src, dport, sport)
        w.writerow([*key, *flows[key], 'true' if reverse in flows else 'false'])
PY
python3 /tmp/solve_flow_ledger.py

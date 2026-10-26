#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_inventory.py <<'PY'
import hashlib
import ipaddress
import json
import struct
from collections import defaultdict

raw = open('telemetry.pcap', 'rb').read()
streams = defaultdict(list)
pos = 24
while pos < len(raw):
    size = struct.unpack_from('<I', raw, pos + 8)[0]
    frame = raw[pos + 16:pos + 16 + size]
    pos += 16 + size
    ip = frame[14:]
    tcp = ip[(ip[0] & 15) * 4:]
    sport, dport, seq = struct.unpack_from('!HHI', tcp)
    content = tcp[(tcp[12] >> 4) * 4:]
    if dport == 80 and content:
        source = str(ipaddress.IPv4Address(ip[12:16]))
        streams[(source, sport)].append((seq, content))
answer = []
for (source, port), chunks in streams.items():
    request = b''.join(chunk for _, chunk in sorted(chunks))
    header, rest = request.split(b'\r\n\r\n', 1)
    lines = header.decode('ascii').split('\r\n')
    method, uri = lines[0].split()[:2]
    length = int(next(line.split(':', 1)[1] for line in lines[1:]
                      if line.lower().startswith('content-length:')))
    body = rest[:length]
    answer.append(dict(src_ip=source, src_port=port, method=method, uri=uri,
                       body_bytes=len(body), body_sha256=hashlib.sha256(body).hexdigest()))
with open('request_inventory.json', 'w') as f:
    json.dump(sorted(answer, key=lambda row: row['src_port']), f)
PY
python /tmp/solve_inventory.py

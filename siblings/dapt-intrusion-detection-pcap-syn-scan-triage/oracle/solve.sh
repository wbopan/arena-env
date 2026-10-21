#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json, math, struct
from collections import Counter, defaultdict
data = open('capture.pcap', 'rb').read()
e = '<' if struct.unpack('<I', data[:4])[0] == 0xa1b2c3d4 else '>'
off = 24
ports = defaultdict(Counter); syn = Counter(); tot = Counter()
while off + 16 <= len(data):
    incl = struct.unpack(e + 'IIII', data[off:off + 16])[2]
    fr = data[off + 16:off + 16 + incl]
    off += 16 + incl
    if len(fr) < 34 or fr[12:14] != bytes([8, 0]) or fr[23] != 6:
        continue
    t = 14 + (fr[14] & 15) * 4
    src = '.'.join(map(str, fr[26:30]))
    dport = int.from_bytes(fr[t + 2:t + 4], 'big')
    fl = fr[t + 13]
    tot[src] += 1
    ports[src][dport] += 1
    if (fl & 2) and not (fl & 16):
        syn[src] += 1
srcs = []
for s in sorted(tot, key=lambda x: tuple(int(p) for p in x.split('.'))):
    n = tot[s]
    if n < 30:
        continue
    c = ports[s]
    h = -sum(v / n * math.log2(v / n) for v in c.values())
    r = syn[s] / n
    srcs.append({'src_ip': s, 'tcp_packets': n, 'unique_dst_ports': len(c),
                 'port_entropy': round(h, 4), 'syn_only_ratio': round(r, 4),
                 'is_scanner': bool(h > 5.0 and r > 0.7 and len(c) > 40)})
out = {'sources': srcs, 'scanners': [x['src_ip'] for x in srcs if x['is_scanner']]}
with open('scan_report.json', 'w') as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/solve.py

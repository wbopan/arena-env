#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, math
from collections import defaultdict
g = defaultdict(list)
with open('traffic.csv', newline='') as f:
    for r in csv.DictReader(f):
        if r['src_ip'] and r['dst_ip']:
            g[(r['src_ip'], r['dst_ip'])].append((float(r['ts']), int(r['length'])))
with open('beacon_report.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['src_ip', 'dst_ip', 'packets', 'total_bytes', 'iat_mean', 'iat_cv', 'is_beacon'])
    for k in sorted(g):
        v = g[k]
        if len(v) < 10:
            continue
        ts = sorted(t for t, _ in v)
        iats = [b - a for a, b in zip(ts, ts[1:])]
        m = sum(iats) / len(iats)
        sd = math.sqrt(sum((x - m) ** 2 for x in iats) / len(iats))
        cv = sd / m if m > 0 else 0.0
        w.writerow([k[0], k[1], len(v), sum(l for _, l in v), round(m, 3), round(cv, 4), 'true' if cv < 0.5 else 'false'])
EOF
python3 /tmp/solve.py

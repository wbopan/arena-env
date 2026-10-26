#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_ip_roles.py <<'PY'
import csv
from collections import defaultdict

sent, recv = defaultdict(int), defaultdict(int)
outs, ins = defaultdict(set), defaultdict(set)
with open('/root/work/traffic.csv', newline='') as f:
    for p in csv.DictReader(f):
        a, b = p['src_ip'], p['dst_ip']
        if not (a and b):
            continue
        n = int(p['length'])
        sent[a] += n
        recv[b] += n
        outs[a].add(b)
        ins[b].add(a)
with open('/root/work/ip_roles.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['ip', 'bytes_sent', 'bytes_recv', 'pcr', 'outdegree', 'indegree', 'role'])
    for ip in sorted(sent.keys() | recv.keys()):
        s, r = sent[ip], recv[ip]
        pcr = (s-r)/(s+r)
        role = 'producer' if pcr > .2 else 'consumer' if pcr < -.2 else 'balanced'
        w.writerow([ip, s, r, f'{pcr:.6f}', len(outs[ip]), len(ins[ip]), role])
PY
python3 /tmp/solve_ip_roles.py

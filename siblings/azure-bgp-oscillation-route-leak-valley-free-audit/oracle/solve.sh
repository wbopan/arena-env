#!/bin/bash
set -e
cat > /tmp/solve_leak.py <<'EOF'
import csv, json
inv = {'customer': 'provider', 'provider': 'customer', 'peer': 'peer'}
rel = {}
with open('/root/work/relationships.csv', newline='') as f:
    for r in csv.DictReader(f):
        a, b, t = int(r['as_a']), int(r['as_b']), r['relationship'].strip()
        rel[(a, b)] = t
        rel[(b, a)] = inv[t]
props = json.load(open('/root/work/propagations.json'))
out = []
for p in sorted(props, key=lambda x: x['path_id']):
    path = p['as_path']
    for i in range(1, len(path) - 1):
        s, l, d = path[i - 1], path[i], path[i + 1]
        st, dt = rel[(l, s)], rel[(l, d)]
        if st in ('provider', 'peer') and dt in ('provider', 'peer'):
            out.append([p['path_id'], p['prefix'], l, s, d, st, dt])
with open('/root/work/route_leaks.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['path_id', 'prefix', 'leaker_as', 'source_as', 'destination_as', 'source_type', 'destination_type'])
    w.writerows(out)
EOF
python3 /tmp/solve_leak.py

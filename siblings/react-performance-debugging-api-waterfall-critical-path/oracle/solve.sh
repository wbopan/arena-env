#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_waterfall.py <<'EOF'
import json

with open('api_routes.json') as f:
    data = json.load(f)

out = []
for r in data['routes']:
    ef = {}
    deps = {}
    for op in r['operations']:
        deps[op['name']] = op['depends_on']
        start = max([ef[d] for d in op['depends_on']], default=0)
        ef[op['name']] = start + op['duration_ms']
    seq = sum(op['duration_ms'] for op in r['operations'])
    opt = max(ef.values())
    cur = min(n for n, v in ef.items() if v == opt)
    path = [cur]
    while deps[cur]:
        m = max(ef[d] for d in deps[cur])
        cur = min(d for d in deps[cur] if ef[d] == m)
        path.append(cur)
    path.reverse()
    out.append({'route': r['route'], 'sequential_ms': seq, 'optimal_ms': opt,
                'saved_ms': seq - opt, 'speedup': round(seq / opt, 3),
                'critical_path': path})

report = {'routes': out, 'total_saved_ms': sum(x['saved_ms'] for x in out)}
with open('waterfall_report.json', 'w') as f:
    json.dump(report, f, indent=2)
EOF
python3 /tmp/solve_waterfall.py

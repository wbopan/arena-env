#!/bin/bash
cd /root/work
cat > /tmp/audit.py <<'EOF'
import json, sys
from collections import deque, defaultdict
sys.setrecursionlimit(10000)
g = json.load(open('dialogue.json'))
ids = [n['id'] for n in g['nodes']]
S = set(ids); start = ids[0]
out = defaultdict(list)
for e in g['edges']:
    out[e['from']].append(e['to'])
seen = {start}; q = deque([(start, 0)]); best = -1
while q:
    u, d = q.popleft()
    for t in out[u]:
        if t == 'End':
            if best < 0 or d + 1 < best: best = d + 1
        elif t in S and t not in seen:
            seen.add(t); q.append((t, d + 1))
memo = {}
def f(v):
    if v not in memo:
        memo[v] = sum(1 if t == 'End' else (f(t) if t in S else 0) for t in out[v])
    return memo[v]
rep = {
    'start': start,
    'reachable_count': len(seen),
    'unreachable': sorted(set(ids) - seen),
    'missing_targets': sorted({e['to'] for e in g['edges'] if e['to'] != 'End' and e['to'] not in S}),
    'dead_ends': sorted(i for i in ids if not out[i]),
    'paths_to_end': f(start),
    'shortest_to_end': best,
}
json.dump(rep, open('report.json', 'w'), indent=2)
EOF
python3 /tmp/audit.py

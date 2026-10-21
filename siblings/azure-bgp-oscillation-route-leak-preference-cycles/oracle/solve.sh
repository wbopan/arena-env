#!/bin/bash
set -e
cat > /tmp/solve_osc.py <<'EOF'
import json
raw = json.load(open('/root/work/preferences.json'))
pref = {int(k): v for k, v in raw.items()}
nxt = {a: (v if v is not None and v in pref else None) for a, v in pref.items()}
state = {}
members = set()
for s in pref:
    if s in state:
        continue
    path = []
    pos = {}
    cur = s
    while cur is not None and cur not in state and cur not in pos:
        pos[cur] = len(path)
        path.append(cur)
        cur = nxt[cur]
    if cur is not None and cur in pos:
        members.update(path[pos[cur]:])
    for a in path:
        state[a] = 1
cycles = []
seen = set()
for a in sorted(members):
    if a in seen:
        continue
    c = [a]
    b = nxt[a]
    while b != a:
        c.append(b)
        b = nxt[b]
    seen.update(c)
    cycles.append(c)
memo = {}
def reaches(a):
    chain = []
    cur = a
    res = False
    while cur is not None:
        if cur in memo:
            res = memo[cur]
            break
        if cur in members:
            res = True
            break
        chain.append(cur)
        cur = nxt[cur]
    for x in chain:
        memo[x] = res
    return res or a in members
affected = sorted(a for a in pref if reaches(a))
stable = sorted(a for a in pref if a not in set(affected))
rep = {'oscillation_detected': bool(cycles), 'cycles': cycles,
       'oscillating_ases': sorted(members), 'affected_ases': affected,
       'stable_ases': stable}
json.dump(rep, open('/root/work/oscillation_report.json', 'w'), indent=2)
EOF
python3 /tmp/solve_osc.py

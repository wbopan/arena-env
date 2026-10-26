#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_settlement.py <<'PY'
import json

def cube(x, y):
    a = x - (y - (y & 1)) // 2
    return a, -a-y, y

def dist(a, b):
    return sum(abs(u-v) for u, v in zip(cube(*a), cube(*b))) // 2

d = json.load(open('settlement.json'))
choices = []
for x, y in d['candidates']:
    reached = [t for t in d['tiles'] if dist((x,y), (t['x'],t['y'])) <= 2]
    choices.append((sum(t['weight'] for t in reached), len(reached), x, y))
v, n, x, y = min(choices, key=lambda z: (-z[0], z[3], z[2]))
with open('settlement_answer.json', 'w') as f:
    json.dump({'center':[x,y], 'value':v, 'worked_count':n}, f)
PY
python /tmp/solve_settlement.py

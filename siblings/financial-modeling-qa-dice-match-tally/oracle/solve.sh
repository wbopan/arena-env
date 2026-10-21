#!/bin/bash
set -e
cat > /tmp/solve.py <<'EOF'
import json
from openpyxl import load_workbook

ws = load_workbook('/root/work/data.xlsx', data_only=True)['Games']

def sc(d):
    s = sorted(d)
    if s[0] == s[2]:
        return 300 + s[0]
    if s[1] - s[0] == 1 and s[2] - s[1] == 1:
        return 200 + s[2]
    if s[0] == s[1] or s[1] == s[2]:
        kicker = s[0] if s[1] == s[2] else s[2]
        return 100 + 10 * s[1] + kicker
    return sum(s)

scores = {}
for r in ws.iter_rows(min_row=2, values_only=True):
    if r[0] is not None:
        scores[int(r[0])] = sc([int(r[1]), int(r[2]), int(r[3])])

p1 = p2 = t = 0
for g in range(1, max(scores) + 1, 2):
    a, b = scores[g], scores[g + 1]
    if a > b:
        p1 += 1
    elif b > a:
        p2 += 1
    else:
        t += 1

with open('/root/work/answer.json', 'w') as f:
    json.dump({'player1_wins': p1, 'player2_wins': p2, 'ties': t, 'difference': p1 - p2}, f)
EOF
python3 /tmp/solve.py

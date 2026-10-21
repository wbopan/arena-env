#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_dots.py <<'EOF'
import csv, json
M = (-0.0000010930, 0.0007391293, -0.1918759221, 24.0900756, -307.75076, 40, 210)
F = (-0.0000010706, 0.0005158568, -0.1126655495, 13.6175032, -57.96288, 40, 150)
def dots(sex, bw, tot):
    a, b, c, d, e, lo, hi = F if sex == 'F' else M
    x = min(max(bw, lo), hi)
    return tot * 500 / (a * x**4 + b * x**3 + c * x**2 + d * x + e)
teams = {}
with open('lifters.csv', newline='') as f:
    for r in csv.DictReader(f):
        vals = [float(r[k]) if r[k].strip() else 0.0 for k in ('Best3SquatKg', 'Best3BenchKg', 'Best3DeadliftKg')]
        s = dots(r['Sex'], float(r['BodyweightKg']), sum(vals)) if min(vals) > 0 else 0.0
        teams.setdefault(r['Team'], []).append((s, r['Name']))
out = []
for t, m in teams.items():
    m.sort(key=lambda z: (-z[0], z[1]))
    top = m[:3]
    out.append({'team': t, 'score': round(sum(z[0] for z in top), 2), 'top_lifters': [z[1] for z in top]})
out.sort(key=lambda o: (-o['score'], o['team']))
res = [{'rank': i, **o} for i, o in enumerate(out, 1)]
with open('team_standings.json', 'w') as f:
    json.dump(res, f, indent=2)
EOF
python3 /tmp/solve_dots.py

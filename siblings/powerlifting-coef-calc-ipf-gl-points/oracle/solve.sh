#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_gl.py <<'EOF'
import csv, math
import pandas as pd
P = {
    ('SBD', 'M', 'Raw'): (1199.72839, 1025.18162, 0.009210),
    ('SBD', 'M', 'Single'): (1236.25115, 1449.21864, 0.01644),
    ('SBD', 'F', 'Raw'): (610.32796, 1045.59282, 0.03048),
    ('SBD', 'F', 'Single'): (758.63878, 949.31382, 0.02435),
    ('B', 'M', 'Raw'): (320.98041, 281.40258, 0.01008),
    ('B', 'M', 'Single'): (381.22073, 733.79378, 0.02398),
    ('B', 'F', 'Raw'): (142.40398, 442.52671, 0.04724),
    ('B', 'F', 'Single'): (221.82209, 357.00377, 0.02937),
}
df = pd.read_excel('meet.xlsx', sheet_name='Results')
out = []
for _, r in df.iterrows():
    v = lambda c: float(r[c]) if pd.notna(r[c]) else 0.0
    sq, bp, dl = v('Best3SquatKg'), v('Best3BenchKg'), v('Best3DeadliftKg')
    ev = r['Event']
    if ev == 'SBD':
        tot = sq + bp + dl if min(sq, bp, dl) > 0 else 0.0
    else:
        tot = bp if bp > 0 else 0.0
    sex = 'F' if r['Sex'] == 'F' else 'M'
    eq = 'Raw' if r['Equipment'] in ('Raw', 'Wraps') else 'Single'
    a, b, c = P[(ev, sex, eq)]
    bw = float(r['BodyweightKg'])
    gl = 0.0
    if bw >= 35 and tot > 0:
        den = a - b * math.exp(-c * bw)
        if den != 0:
            gl = tot * max(0.0, 100.0 / den)
    out.append((str(r['Name']), ev, round(tot, 1), round(gl, 2)))
out.sort(key=lambda z: (-z[3], z[0]))
with open('gl_points.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Name', 'Event', 'TotalKg', 'GLPoints'])
    for z in out:
        w.writerow([z[0], z[1], f'{z[2]:.1f}', f'{z[3]:.2f}'])
EOF
python3 /tmp/solve_gl.py

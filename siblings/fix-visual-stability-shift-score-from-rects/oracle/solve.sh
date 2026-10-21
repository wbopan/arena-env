#!/bin/bash
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json, csv
d = json.load(open('frames.json'))
W = d['viewport']['width']; H = d['viewport']['height']
def clip(r):
    return (max(r['x'], 0), max(r['y'], 0), min(r['x'] + r['width'], W), min(r['y'] + r['height'], H))
def area(b):
    return max(0, b[2] - b[0]) * max(0, b[3] - b[1])
rows = []
for fr in d['frames']:
    p, c = fr['previous'], fr['current']
    a, b = clip(p), clip(c)
    i = (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))
    imp = (area(a) + area(b) - area(i)) / (W * H)
    df = min(1.0, max(abs(c['x'] - p['x']), abs(c['y'] - p['y'])) / max(W, H))
    rows.append((fr['id'], imp, df, imp * df))
rows.sort(key=lambda r: r[0])
with open('shift_scores.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'impact_fraction', 'distance_fraction', 'score'])
    for r in rows:
        w.writerow([r[0], f'{r[1]:.6f}', f'{r[2]:.6f}', f'{r[3]:.6f}'])
EOF
python3 /tmp/solve.py

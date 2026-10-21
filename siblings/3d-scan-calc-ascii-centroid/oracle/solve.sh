#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_centroid.py <<'EOF'
import json
import numpy as np

verts = []
for line in open('part.stl'):
    t = line.split()
    if t and t[0] == 'vertex':
        verts.append(tuple(round(float(x), 4) for x in t[1:4]))
n = len(verts) // 3
parent = list(range(n))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

first = {}
for i in range(n):
    for k in range(3):
        key = verts[3 * i + k]
        if key in first:
            ra, rb = find(i), find(first[key])
            if ra != rb:
                parent[ra] = rb
        else:
            first[key] = i

groups = {}
for i in range(n):
    groups.setdefault(find(i), []).append(i)

P = np.array(verts, dtype=float).reshape(n, 3, 3)
best = None
for idx in groups.values():
    T = P[idx]
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    d = np.einsum('ij,ij->i', a, np.cross(b, c))
    vol = d.sum() / 6.0
    if best is None or abs(vol) > abs(best[0]):
        best = (vol, d, T)
vol, d, T = best
cen = (d[:, None] * (T.sum(axis=1) / 4.0)).sum(axis=0) / d.sum()
pts = T.reshape(-1, 3)
out = {
    'volume_cm3': round(abs(float(vol)) / 1000.0, 4),
    'centroid_mm': [round(float(x), 3) for x in cen],
    'bbox_min_mm': [round(float(x), 3) for x in pts.min(axis=0)],
    'bbox_max_mm': [round(float(x), 3) for x in pts.max(axis=0)],
    'debris_count': len(groups) - 1,
}
with open('part_props.json', 'w') as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/solve_centroid.py

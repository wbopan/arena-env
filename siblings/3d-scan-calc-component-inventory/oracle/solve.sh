#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_components.py <<'EOF'
import struct
import numpy as np

data = open('build_plate.stl', 'rb').read()
n = struct.unpack_from('<I', data, 80)[0]
dt = np.dtype([('n', '<f4', (3,)), ('v', '<f4', (3, 3)), ('a', '<u2')])
rec = np.frombuffer(data, dtype=dt, count=n, offset=84)
V = rec['v'].astype(np.float64)
A = rec['a'].astype(int)

dens = {}
for line in open('materials.md'):
    cells = [c.strip() for c in line.strip().strip('|').split('|')]
    if len(cells) >= 3 and cells[0].isdigit():
        dens[int(cells[0])] = float(cells[2])

parent = list(range(n))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

first = {}
for i in range(n):
    for k in range(3):
        key = tuple(V[i, k])
        if key in first:
            ra, rb = find(i), find(first[key])
            if ra != rb:
                parent[ra] = rb
        else:
            first[key] = i

groups = {}
for i in range(n):
    groups.setdefault(find(i), []).append(i)

rows = []
for idx in groups.values():
    T = V[idx]
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    vol = abs(np.einsum('ij,ij->i', a, np.cross(b, c)).sum()) / 6.0
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1).sum()
    mid = int(A[idx[0]])
    rows.append((vol, mid, len(idx), area, vol / 1000.0 * dens[mid]))
rows.sort(key=lambda r: -r[0])
with open('components.csv', 'w') as f:
    f.write('rank,material_id,triangles,volume_mm3,area_mm2,mass_g\n')
    for r, (vol, mid, nt, area, mass) in enumerate(rows, 1):
        f.write(f'{r},{mid},{nt},{vol:.3f},{area:.3f},{mass:.4f}\n')
EOF
python3 /tmp/solve_components.py

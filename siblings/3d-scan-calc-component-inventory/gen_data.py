import struct

import numpy as np
from scipy.spatial import ConvexHull

rng = np.random.default_rng(73411)
MATS = [(3, 'PLA', 1.24), (7, 'PETG', 1.27), (12, 'ABS', 1.04), (18, 'Nylon PA12', 1.01),
        (31, 'Aluminium 6061', 2.70), (44, 'Stainless 316L', 7.98), (56, 'Titanium Ti-6Al-4V', 4.43)]
IDS = [m[0] for m in MATS]


def hull_tris(center, scale, n, mid):
    pts = (rng.normal(size=(n, 3)) * scale + center).astype(np.float32).astype(np.float64)
    h = ConvexHull(pts)
    inner = pts[h.vertices].mean(axis=0)
    out = []
    for s in h.simplices:
        a, b, c = pts[s[0]], pts[s[1]], pts[s[2]]
        nrm = np.cross(b - a, c - a)
        if np.dot(nrm, (a + b + c) / 3 - inner) < 0:
            b, c = c, b
            nrm = -nrm
        out.append((nrm / np.linalg.norm(nrm), a, b, c, mid))
    return out


tris = []
for i in range(4):
    center = np.array([i * 70.0 + rng.uniform(-5, 5), rng.uniform(-20, 20), rng.uniform(10, 20)])
    scale = rng.uniform(6, 18, size=3)
    tris += hull_tris(center, scale, int(rng.integers(14, 23)), int(rng.choice(IDS)))
for j in range(4):
    center = np.array([j * 70.0 + 35.0, rng.uniform(40, 60), rng.uniform(0, 5)])
    tris += hull_tris(center, rng.uniform(1.0, 2.0, size=3), 5, int(rng.choice(IDS)))
order = rng.permutation(len(tris))

with open('build_plate.stl', 'wb') as f:
    f.write(b'build plate scan export'.ljust(80, b' '))
    f.write(struct.pack('<I', len(tris)))
    for k in order:
        nrm, a, b, c, mid = tris[k]
        f.write(struct.pack('<12fH', *nrm, *a, *b, *c, mid))

with open('materials.md', 'w') as f:
    f.write('# Material density table\n\n| Material ID | Material | Density (g/cm^3) |\n|---|---|---|\n')
    for mid, name, rho in MATS:
        f.write(f'| {mid} | {name} | {rho:.2f} |\n')

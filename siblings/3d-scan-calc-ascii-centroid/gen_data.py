import numpy as np
from scipy.spatial import ConvexHull

rng = np.random.default_rng(5150)


def hull_facets(center, scale, n):
    pts = np.round(rng.normal(size=(n, 3)) * scale + center, 4)
    h = ConvexHull(pts)
    inner = pts[h.vertices].mean(axis=0)
    out = []
    for s in h.simplices:
        a, b, c = pts[s[0]], pts[s[1]], pts[s[2]]
        nrm = np.cross(b - a, c - a)
        if np.dot(nrm, (a + b + c) / 3 - inner) < 0:
            b, c = c, b
            nrm = -nrm
        out.append((nrm / np.linalg.norm(nrm), a, b, c))
    return out


main_c = np.array([rng.uniform(20, 60), rng.uniform(-30, 30), rng.uniform(5, 15)])
facets = hull_facets(main_c, rng.uniform([8, 6, 4], [16, 12, 8]), 20)
for _ in range(int(rng.integers(3, 8))):
    d = rng.normal(size=3)
    d /= np.linalg.norm(d)
    facets += hull_facets(main_c + d * rng.uniform(55, 85), rng.uniform(0.6, 1.5, size=3), 5)
order = rng.permutation(len(facets))
lines = ['solid scan_part']
for k in order:
    nrm, a, b, c = facets[k]
    lines.append('  facet normal %.4f %.4f %.4f' % tuple(nrm))
    lines.append('    outer loop')
    for p in (a, b, c):
        lines.append('      vertex %.4f %.4f %.4f' % tuple(p))
    lines.append('    endloop')
    lines.append('  endfacet')
lines.append('endsolid scan_part')
with open('part.stl', 'w') as f:
    f.write('\n'.join(lines) + '\n')

#!/bin/bash
set -e
cat > /tmp/solve.py << 'EOF'
import json, os
import numpy as np

d = json.load(open('/root/work/scene.json'))
geo = {g['uuid']: g for g in d['geometries']}
parts = {}


def walk(n, PW, owner):
    M = np.array(n['matrix'], float).reshape(4, 4).T if 'matrix' in n else np.eye(4)
    W = PW @ M
    if n.get('type') == 'Group' and n.get('name'):
        owner = n['name']
        parts.setdefault(owner, [])
    if n.get('type') == 'Mesh' and owner is not None:
        g = geo[n['geometry']]
        c = np.array([[sx * g['width'] / 2, sy * g['height'] / 2, sz * g['depth'] / 2, 1.0]
                      for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
        parts[owner].append((W @ c.T).T[:, :3])
    for ch in n.get('children', []):
        walk(ch, W, owner)


walk(d['object'], np.eye(4), None)
F = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1),
     (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
out = '/root/work/output/links'
os.makedirs(out, exist_ok=True)
for name, boxes in sorted(parts.items()):
    if not boxes:
        continue
    lines = ['o ' + name]
    for pts in boxes:
        for p in pts:
            lines.append('v %.6f %.6f %.6f' % tuple(p))
    for b in range(len(boxes)):
        for a, bb, cc in F:
            lines.append('f %d %d %d' % (8 * b + a + 1, 8 * b + bb + 1, 8 * b + cc + 1))
    with open(os.path.join(out, name + '.obj'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
EOF
python3 /tmp/solve.py

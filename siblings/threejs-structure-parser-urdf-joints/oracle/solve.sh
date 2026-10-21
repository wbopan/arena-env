#!/bin/bash
set -e
cat > /tmp/solve.py << 'EOF'
import json, os
import numpy as np

REV = ('hinge', 'wheel', 'knob', 'spin', 'rotate')
PRI = ('slide', 'slider', 'rail', 'drawer', 'track')
d = json.load(open('/root/work/scene.json'))
W, par = {}, {}


def walk(n, PW, owner):
    M = np.array(n['matrix'], float).reshape(4, 4).T if 'matrix' in n else np.eye(4)
    Wn = PW @ M
    if n.get('type') == 'Group' and n.get('name'):
        W[n['name']] = Wn
        par[n['name']] = owner
        owner = n['name']
    for c in n.get('children', []):
        walk(c, Wn, owner)


walk(d['object'], np.eye(4), None)
lines = ['<?xml version="1.0"?>', '<robot name="object">']
for l in sorted(W):
    lines.append('  <link name="%s"><visual><geometry><mesh filename="meshes/%s.obj"/></geometry></visual></link>' % (l, l))
for c in sorted(k for k in par if par[k] is not None):
    p = par[c]
    t = (np.linalg.inv(W[p]) @ W[c])[:3, 3]
    lc = c.lower()
    if any(k in lc for k in REV):
        typ = 'revolute'
    elif any(k in lc for k in PRI):
        typ = 'prismatic'
    else:
        typ = 'fixed'
    lines.append('  <joint name="joint_%s" type="%s"><parent link="%s"/><child link="%s"/><origin xyz="%.4f %.4f %.4f"/></joint>' % (c, typ, p, c, t[0], t[1], t[2]))
lines.append('</robot>')
os.makedirs('/root/work/output', exist_ok=True)
with open('/root/work/output/object.urdf', 'w') as f:
    f.write('\n'.join(lines) + '\n')
EOF
python3 /tmp/solve.py

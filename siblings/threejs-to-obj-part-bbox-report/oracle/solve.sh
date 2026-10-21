#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import json
import numpy as np

s = json.load(open('scene.json'))
G = s['geometries']

def R(r):
    a, b, c = r
    ca, sa, cb, sb, cc, sc = np.cos(a), np.sin(a), np.cos(b), np.sin(b), np.cos(c), np.sin(c)
    X = np.array([[1,0,0],[0,ca,-sa],[0,sa,ca]])
    Y = np.array([[cb,0,sb],[0,1,0],[-sb,0,cb]])
    Z = np.array([[cc,-sc,0],[sc,cc,0],[0,0,1]])
    return X @ Y @ Z

def local(n):
    M = np.eye(4)
    M[:3,:3] = R(n['rotation']) @ np.diag(n['scale'])
    M[:3,3] = n['position']
    return M

ZUP = np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]], float)
parts = {}

def walk(n, P, owner):
    W = P @ local(n)
    if n['type'] == 'Group' and n.get('name'):
        owner = n['name']
    if n['type'] in ('Mesh', 'InstancedMesh') and owner:
        g = G[n['geometry']]
        V = np.array(g['vertices'], float)
        H = np.c_[V, np.ones(len(V))]
        mats = [W] if n['type'] == 'Mesh' else [W @ local(i) for i in n['instances']]
        e = parts.setdefault(owner, {'o': 0, 'v': 0, 't': 0, 'pts': []})
        for M in mats:
            e['o'] += 1
            e['v'] += len(V)
            e['t'] += len(g['faces'])
            e['pts'].append((ZUP @ M @ H.T).T[:, :3])
    for c in n.get('children', []):
        walk(c, W, owner)

walk(s['root'], np.eye(4), None)
out = []
for name in sorted(parts):
    e = parts[name]
    P = np.vstack(e['pts'])
    out.append({'name': name, 'object_count': e['o'], 'vertex_count': e['v'],
                'triangle_count': e['t'],
                'bbox_min': [round(float(x), 4) for x in P.min(0)],
                'bbox_max': [round(float(x), 4) for x in P.max(0)]})
json.dump({'parts': out}, open('/root/work/parts.json', 'w'), indent=2)
EOF
python3 /tmp/solve.py

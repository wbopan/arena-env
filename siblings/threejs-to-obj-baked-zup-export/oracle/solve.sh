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
lines = []
off = [0]

def walk(n, P):
    W = P @ local(n)
    if n['type'] == 'Mesh':
        g = G[n['geometry']]
        V = np.array(g['vertices'], float)
        H = np.c_[V, np.ones(len(V))]
        Q = (ZUP @ W @ H.T).T[:, :3]
        lines.append('o ' + n['name'])
        for p in Q:
            lines.append('v %.6f %.6f %.6f' % tuple(p))
        for f in g['faces']:
            lines.append('f ' + ' '.join(str(off[0] + i + 1) for i in f))
        off[0] += len(V)
    for c in n.get('children', []):
        walk(c, W)

walk(s['root'], np.eye(4))
open('/root/work/object.obj', 'w').write('\n'.join(lines) + '\n')
EOF
python3 /tmp/solve.py

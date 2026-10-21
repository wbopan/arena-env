import json
import math
import random

import numpy as np

random.seed(9090)
_c = [0]


def uid():
    _c[0] += 1
    return '%08x-77aa-4c00-8b00-%012x' % ((_c[0] * 2654435761) % (1 << 32), _c[0])


def rand_matrix(tscale):
    ax = np.array([random.uniform(-1, 1) for _ in range(3)])
    ax /= np.linalg.norm(ax)
    ang = random.uniform(-math.pi, math.pi)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    R = np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * (K @ K)
    s = random.uniform(0.7, 1.4) if random.random() < 0.3 else 1.0
    M = np.eye(4)
    M[:3, :3] = R * s
    M[:3, 3] = [random.uniform(-tscale, tscale) for _ in range(3)]
    return [round(float(x), 6) for x in M.T.reshape(-1)]


geometries = []
MAT = uid()
_m = [0]


def node(typ, name, tscale):
    return {'uuid': uid(), 'type': typ, 'name': name, 'layers': 1,
            'matrix': rand_matrix(tscale), 'up': [0, 1, 0], 'children': []}


def mesh(prefix):
    g = {'uuid': uid(), 'type': 'BoxGeometry',
         'width': round(random.uniform(0.05, 0.6), 3),
         'height': round(random.uniform(0.05, 0.6), 3),
         'depth': round(random.uniform(0.05, 0.6), 3),
         'widthSegments': 1, 'heightSegments': 1, 'depthSegments': 1}
    geometries.append(g)
    m = node('Mesh', '%s_box%d' % (prefix, _m[0]), 0.4)
    _m[0] += 1
    m.pop('children')
    m['geometry'] = g['uuid']
    m['material'] = MAT
    return m


root = node('Object3D', '', 0.5)
base = node('Group', 'base', 0.5)
root['children'].append(base)
root['children'].append(mesh('loose'))
base['children'].append(mesh('base'))
links = [base]
pool = ['lid_hinge', 'front_wheel', 'rear_wheel', 'dial_knob', 'spin_top', 'tray_slide',
        'top_drawer', 'guide_rail', 'belt_track', 'handle', 'panel', 'bracket', 'cover']
for i, nm in enumerate(random.sample(pool, 8)):
    parent = random.choice(links)
    r = random.random()
    if r < 0.55:
        w = node('Group', '', 0.5) if r < 0.3 else node('Object3D', 'mount_%d' % i, 0.5)
        parent['children'].append(w)
        if random.random() < 0.5:
            w['children'].append(mesh(parent['name']))
        if random.random() < 0.3:
            w2 = node('Object3D', '', 0.3)
            w['children'].append(w2)
            w = w2
        holder = w
    else:
        holder = parent
    g = node('Group', nm, 0.6)
    holder['children'].append(g)
    for _ in range(random.randint(1, 2)):
        g['children'].append(mesh(nm))
    links.append(g)

scene = {'metadata': {'version': 4.6, 'type': 'Object', 'generator': 'Object3D.toJSON'},
         'geometries': geometries,
         'materials': [{'uuid': MAT, 'type': 'MeshStandardMaterial', 'color': 13421772}],
         'object': root}
with open('scene.json', 'w') as f:
    json.dump(scene, f)

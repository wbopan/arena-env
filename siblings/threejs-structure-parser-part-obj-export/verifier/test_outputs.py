import glob
import json
import os

import numpy as np

WORK = '/root/work'
OUT = os.path.join(WORK, 'output', 'links')
TOL = 1e-3


def expected_parts():
    with open(os.path.join(WORK, 'scene.json')) as f:
        d = json.load(f)
    geo = {g['uuid']: g for g in d['geometries']}
    parts = {}

    def walk(n, PW, owner):
        m = n.get('matrix')
        M = np.array(m, float).reshape(4, 4).T if m else np.eye(4)
        W = PW @ M
        if n.get('type') == 'Group' and n.get('name'):
            owner = n['name']
            parts.setdefault(owner, [])
        if n.get('type') == 'Mesh' and owner is not None:
            g = geo[n['geometry']]
            pts = np.array([[sx * g['width'] / 2, sy * g['height'] / 2, sz * g['depth'] / 2, 1.0]
                            for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
            parts[owner].append((W @ pts.T).T[:, :3])
        for c in n.get('children', []):
            walk(c, W, owner)

    walk(d['object'], np.eye(4), None)
    return {k: v for k, v in parts.items() if v}


def parse_obj(path):
    vs, fs = [], []
    with open(path) as f:
        for line in f:
            t = line.split()
            if not t:
                continue
            if t[0] == 'v':
                vs.append([float(x) for x in t[1:4]])
            elif t[0] == 'f':
                fs.append([int(x.split('/')[0]) for x in t[1:]])
    return np.array(vs, float).reshape(-1, 3), fs


EXP = expected_parts()


def test_output_dir_exists():
    assert os.path.isdir(OUT), 'missing output/links directory'


def test_part_file_set():
    names = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(OUT, '*.obj'))}
    assert names == set(EXP), 'part set mismatch: got %s expected %s' % (sorted(names), sorted(EXP))


def test_vertex_and_face_counts():
    for name, boxes in EXP.items():
        v, fs = parse_obj(os.path.join(OUT, name + '.obj'))
        assert len(v) == 8 * len(boxes), '%s: vertex count %d' % (name, len(v))
        assert len(fs) == 12 * len(boxes), '%s: face count %d' % (name, len(fs))
        for face in fs:
            assert len(face) == 3, '%s: non-triangle face' % name
            assert all(1 <= i <= len(v) for i in face), '%s: bad face index' % name


def test_world_space_vertices():
    for name, boxes in EXP.items():
        v, _ = parse_obj(os.path.join(OUT, name + '.obj'))
        e = np.vstack(boxes)
        assert len(v) == len(e)
        dist = np.linalg.norm(v[:, None, :] - e[None, :, :], axis=2)
        assert dist.min(axis=1).max() < TOL, '%s: output vertex not in expected set' % name
        assert dist.min(axis=0).max() < TOL, '%s: expected vertex missing' % name

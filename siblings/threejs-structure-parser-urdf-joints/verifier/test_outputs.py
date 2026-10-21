import json
import os
import xml.etree.ElementTree as ET

import numpy as np

WORK = '/root/work'
URDF = os.path.join(WORK, 'output', 'object.urdf')
REV = ('hinge', 'wheel', 'knob', 'spin', 'rotate')
PRI = ('slide', 'slider', 'rail', 'drawer', 'track')
TOL = 1e-3


def expected():
    with open(os.path.join(WORK, 'scene.json')) as f:
        d = json.load(f)
    W, par = {}, {}

    def walk(n, PW, owner):
        m = n.get('matrix')
        M = np.array(m, float).reshape(4, 4).T if m else np.eye(4)
        Wn = PW @ M
        if n.get('type') == 'Group' and n.get('name'):
            W[n['name']] = Wn
            par[n['name']] = owner
            owner = n['name']
        for c in n.get('children', []):
            walk(c, Wn, owner)

    walk(d['object'], np.eye(4), None)
    joints = {}
    for c, p in par.items():
        if p is None:
            continue
        xyz = (np.linalg.inv(W[p]) @ W[c])[:3, 3]
        lc = c.lower()
        if any(k in lc for k in REV):
            t = 'revolute'
        elif any(k in lc for k in PRI):
            t = 'prismatic'
        else:
            t = 'fixed'
        joints['joint_' + c] = (p, c, t, xyz)
    return set(W), joints


LINKS, JOINTS = expected()


def load():
    assert os.path.exists(URDF), 'missing output/object.urdf'
    root = ET.parse(URDF).getroot()
    assert root.tag == 'robot' and root.get('name') == 'object'
    return root


def test_urdf_parses():
    load()


def test_links_and_meshes():
    root = load()
    links = root.findall('link')
    assert {l.get('name') for l in links} == LINKS
    for l in links:
        mesh = l.find('visual/geometry/mesh')
        assert mesh is not None, 'link %s has no mesh' % l.get('name')
        assert mesh.get('filename') == 'meshes/%s.obj' % l.get('name')


def test_joint_topology():
    root = load()
    got = {}
    for j in root.findall('joint'):
        got[j.get('name')] = (j.find('parent').get('link'), j.find('child').get('link'))
    exp = {k: (v[0], v[1]) for k, v in JOINTS.items()}
    assert got == exp


def test_joint_types():
    root = load()
    for j in root.findall('joint'):
        assert j.get('type') == JOINTS[j.get('name')][2], 'wrong type for %s' % j.get('name')


def test_joint_origins():
    root = load()
    for j in root.findall('joint'):
        o = j.find('origin')
        assert o is not None, 'missing origin in %s' % j.get('name')
        xyz = np.array([float(x) for x in o.get('xyz').split()])
        assert np.abs(xyz - JOINTS[j.get('name')][3]).max() < TOL, 'origin mismatch for %s' % j.get('name')


def test_sorted_order():
    root = load()
    tags = [c.tag for c in root if c.tag in ('link', 'joint')]
    nl = tags.count('link')
    assert tags == ['link'] * nl + ['joint'] * (len(tags) - nl), 'links must precede joints'
    ln = [l.get('name') for l in root.findall('link')]
    jn = [j.get('name') for j in root.findall('joint')]
    assert ln == sorted(ln) and jn == sorted(jn)

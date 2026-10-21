import json
import os

import numpy as np
import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "object.obj")


def rot(r):
    a, b, c = r
    X = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
    Y = np.array([[np.cos(b), 0, np.sin(b)], [0, 1, 0], [-np.sin(b), 0, np.cos(b)]])
    Zr = np.array([[np.cos(c), -np.sin(c), 0], [np.sin(c), np.cos(c), 0], [0, 0, 1]])
    return X @ Y @ Zr


def mat(n):
    M = np.eye(4)
    M[:3, :3] = rot(n["rotation"]) @ np.diag(n["scale"])
    M[:3, 3] = n["position"]
    return M


def expected():
    with open(os.path.join(WORK, "scene.json")) as fh:
        s = json.load(fh)
    geoms = s["geometries"]
    names, verts, faces = [], [], []

    def visit(node, parent):
        W = parent @ mat(node)
        if node["type"] == "Mesh":
            g = geoms[node["geometry"]]
            base = len(verts)
            for p in g["vertices"]:
                q = W @ np.array([p[0], p[1], p[2], 1.0])
                verts.append([q[0], q[2], -q[1]])
            for f in g["faces"]:
                faces.append([base + i + 1 for i in f])
            names.append(node["name"])
        for c in node.get("children", []):
            visit(c, W)

    visit(s["root"], np.eye(4))
    return names, np.array(verts), faces


def parse():
    names, v, f = [], [], []
    with open(OUT) as fh:
        for line in fh:
            t = line.split()
            if not t:
                continue
            if t[0] == "o":
                names.append(" ".join(t[1:]))
            elif t[0] == "v":
                v.append([float(x) for x in t[1:4]])
            elif t[0] == "f":
                f.append([int(x.split("/")[0]) for x in t[1:]])
    return names, np.array(v), f


def test_output_exists():
    assert os.path.exists(OUT) and os.path.getsize(OUT) > 0


def test_object_order():
    en, _, _ = expected()
    on, _, _ = parse()
    assert on == en


def test_vertex_count():
    _, ev, _ = expected()
    _, ov, _ = parse()
    assert ov.shape == ev.shape


def test_vertex_positions():
    _, ev, _ = expected()
    _, ov, _ = parse()
    assert ov.shape == ev.shape
    assert np.allclose(ov, ev, atol=1e-4), float(np.abs(ov - ev).max())


def test_faces():
    _, _, ef = expected()
    _, _, of = parse()
    assert of == ef

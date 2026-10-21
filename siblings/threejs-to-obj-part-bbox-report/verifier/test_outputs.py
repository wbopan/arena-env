import json
import os

import numpy as np
import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "parts.json")


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
    acc = {}

    def visit(node, parent, owner):
        W = parent @ mat(node)
        if node["type"] == "Group" and node.get("name"):
            owner = node["name"]
        if node["type"] in ("Mesh", "InstancedMesh") and owner is not None:
            g = geoms[node["geometry"]]
            if node["type"] == "Mesh":
                mats = [W]
            else:
                mats = [W @ mat(i) for i in node["instances"]]
            e = acc.setdefault(owner, {"obj": 0, "v": 0, "t": 0, "pts": []})
            for M in mats:
                e["obj"] += 1
                e["v"] += len(g["vertices"])
                e["t"] += len(g["faces"])
                for p in g["vertices"]:
                    q = M @ np.array([p[0], p[1], p[2], 1.0])
                    e["pts"].append([q[0], q[2], -q[1]])
        for c in node.get("children", []):
            visit(c, W, owner)

    visit(s["root"], np.eye(4), None)
    out = {}
    for k, e in acc.items():
        P = np.array(e["pts"])
        out[k] = {"object_count": e["obj"], "vertex_count": e["v"], "triangle_count": e["t"],
                  "bbox_min": P.min(axis=0), "bbox_max": P.max(axis=0)}
    return out


def load():
    with open(OUT) as fh:
        return json.load(fh)["parts"]


def test_output_exists_and_schema():
    assert os.path.exists(OUT)
    parts = load()
    assert isinstance(parts, list) and parts
    for p in parts:
        for k in ("name", "object_count", "vertex_count", "triangle_count", "bbox_min", "bbox_max"):
            assert k in p, k


def test_part_names_sorted():
    exp = expected()
    names = [p["name"] for p in load()]
    assert names == sorted(exp)


def test_counts():
    exp = expected()
    for p in load():
        e = exp[p["name"]]
        assert int(p["object_count"]) == e["object_count"], p["name"]
        assert int(p["vertex_count"]) == e["vertex_count"], p["name"]
        assert int(p["triangle_count"]) == e["triangle_count"], p["name"]


def test_bboxes():
    exp = expected()
    for p in load():
        e = exp[p["name"]]
        assert np.allclose(p["bbox_min"], e["bbox_min"], atol=1e-3), p["name"]
        assert np.allclose(p["bbox_max"], e["bbox_max"], atol=1e-3), p["name"]

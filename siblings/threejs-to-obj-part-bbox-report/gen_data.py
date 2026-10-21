import json, math, random

random.seed(9137)


def r3(p):
    return [round(c, 3) for c in p]


def box(sx, sy, sz):
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    v = [[x, y, z] for x in (-hx, hx) for y in (-hy, hy) for z in (-hz, hz)]
    f = [[0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1],
         [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 5, 7], [1, 7, 3]]
    return {"vertices": [r3(p) for p in v], "faces": f}


def prism(n, r, h):
    v = []
    for y in (0.0, h):
        for k in range(n):
            a = 2 * math.pi * k / n
            v.append([r * math.cos(a), y, r * math.sin(a)])
    f = []
    for k in range(n):
        k2 = (k + 1) % n
        f.append([k, k2, n + k2])
        f.append([k, n + k2, n + k])
    for k in range(1, n - 1):
        f.append([0, k + 1, k])
        f.append([n, n + k, n + k + 1])
    return {"vertices": [r3(p) for p in v], "faces": f}


def pyramid(b, h):
    v = [[-b, 0, -b], [b, 0, -b], [b, 0, b], [-b, 0, b], [0, h, 0]]
    return {"vertices": [r3(p) for p in v],
            "faces": [[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4], [0, 2, 1], [0, 3, 2]]}


geoms = {
    "slab": box(random.uniform(2, 3), random.uniform(0.2, 0.4), random.uniform(1.5, 2.5)),
    "cube": box(random.uniform(0.6, 1.0), random.uniform(0.6, 1.0), random.uniform(0.6, 1.0)),
    "wheel": prism(6, random.uniform(0.3, 0.5), random.uniform(0.1, 0.25)),
    "cone": pyramid(random.uniform(0.3, 0.6), random.uniform(0.6, 1.2)),
}


def tf(small=False):
    p = 1.0 if small else 3.0
    return {
        "position": [round(random.uniform(-p, p), 3) for _ in range(3)],
        "rotation": [round(random.uniform(-math.pi, math.pi), 4) for _ in range(3)],
        "scale": [round(random.uniform(0.6, 1.6), 3) for _ in range(3)],
    }


cnt = [0]


def node(t, name, geom=None, children=None):
    d = {"type": t, "name": name}
    if geom:
        d["geometry"] = geom
    d.update(tf())
    d["children"] = children or []
    return d


def mesh(geom, children=None):
    cnt[0] += 1
    return node("Mesh", f"Mesh_{cnt[0]}", geom, children)


def inst(geom, n):
    cnt[0] += 1
    d = node("InstancedMesh", f"Inst_{cnt[0]}", geom)
    d["instances"] = [tf(small=True) for _ in range(n)]
    return d


gripper = node("Group", "gripper", children=[mesh("cone"), mesh("cube")])
arm = node("Group", "arm", children=[
    node("Group", "", children=[mesh("cube"), mesh("slab")]),
    gripper,
    mesh("cube"),
])
base = node("Group", "base", children=[mesh("slab", children=[mesh("cone")]), arm])
wheels = node("Group", "wheels", children=[inst("wheel", random.randint(3, 6)),
                                          node("Group", "", children=[mesh("wheel")])])
marker = node("Group", "marker", children=[node("Group", "", children=[])])
lamp = node("Group", "lamp", children=[inst("cone", random.randint(2, 4)), mesh("cube")])
kids = [base, wheels, marker, lamp, mesh("slab"), inst("cube", 3)]
random.shuffle(kids)
root = node("Group", "", children=kids)

with open("scene.json", "w") as fh:
    json.dump({"geometries": geoms, "root": root}, fh, indent=1)

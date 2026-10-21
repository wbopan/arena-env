import json, math, random

random.seed(20240611)


def r3(p):
    return [round(c, 3) for c in p]


def box(sx, sy, sz):
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    v = [[x, y, z] for x in (-hx, hx) for y in (-hy, hy) for z in (-hz, hz)]
    f = [[0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1],
         [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 5, 7], [1, 7, 3]]
    return {"vertices": [r3(p) for p in v], "faces": f}


def tetra(s):
    v = [[s, s, s], [-s, -s, s], [-s, s, -s], [s, -s, -s]]
    return {"vertices": [r3(p) for p in v], "faces": [[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]]}


def pyramid(b, h):
    v = [[-b, 0, -b], [b, 0, -b], [b, 0, b], [-b, 0, b], [0, h, 0]]
    return {"vertices": [r3(p) for p in v],
            "faces": [[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4], [0, 2, 1], [0, 3, 2]]}


geoms = {
    "cube": box(random.uniform(0.8, 1.2), random.uniform(0.8, 1.2), random.uniform(0.8, 1.2)),
    "plank": box(random.uniform(1.5, 2.5), random.uniform(0.1, 0.3), random.uniform(0.4, 0.7)),
    "tetra": tetra(random.uniform(0.4, 0.8)),
    "pyramid": pyramid(random.uniform(0.4, 0.9), random.uniform(0.8, 1.6)),
}
gnames = sorted(geoms)


def tf():
    return {
        "position": [round(random.uniform(-3, 3), 3) for _ in range(3)],
        "rotation": [round(random.uniform(-math.pi, math.pi), 4) for _ in range(3)],
        "scale": [round(random.uniform(0.5, 1.8), 3) for _ in range(3)],
    }


counter = [0]


def mesh():
    counter[0] += 1
    d = {"type": "Mesh", "name": f"mesh_{counter[0]:02d}", "geometry": random.choice(gnames)}
    d.update(tf())
    d["children"] = []
    return d


def group(name):
    d = {"type": "Group", "name": name}
    d.update(tf())
    d["children"] = []
    return d


root = group("root")
for i in range(3):
    g = group(f"part_{i}")
    m1 = mesh()
    m1["children"].append(mesh())
    g["children"].append(m1)
    g["children"].append(mesh())
    sub = group(f"part_{i}_sub")
    sub["children"].append(mesh())
    sub["children"].append(mesh())
    g["children"].append(sub)
    random.shuffle(g["children"])
    root["children"].append(g)
root["children"].append(mesh())
random.shuffle(root["children"])

with open("scene.json", "w") as fh:
    json.dump({"geometries": geoms, "root": root}, fh, indent=1)

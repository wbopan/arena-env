import json
import numpy as np

rng = np.random.default_rng(20240607)
segs = [({}, 3), ({"tx": 6.0}, 3), ({"s": 1.05}, 3), ({"ty": -6.0}, 2),
        ({"rot": -0.04}, 2), ({"s": 0.95, "tx": -6.0}, 3),
        ({"rot": 0.035, "ty": 5.0}, 2), ({}, 2)]
order = rng.permutation(len(segs))
params = []
for k in order:
    p, n = segs[int(k)]
    params.extend([p] * n)

lines = ["pair,x0,y0,x1,y1"]
for i, p in enumerate(params):
    j = rng.uniform(0.85, 1.2, size=4)
    s = 1.0 + (p.get("s", 1.0) - 1.0) * j[0]
    rot = p.get("rot", 0.0) * j[1]
    tx = p.get("tx", 0.0) * j[2]
    ty = p.get("ty", 0.0) * j[3]
    pts = rng.uniform(-150, 150, size=(15, 2))
    c, sn = np.cos(rot), np.sin(rot)
    x1 = s * (c * pts[:, 0] - sn * pts[:, 1]) + tx + rng.normal(0, 0.3, 15)
    y1 = s * (sn * pts[:, 0] + c * pts[:, 1]) + ty + rng.normal(0, 0.3, 15)
    for k in range(15):
        lines.append(f"{i},{pts[k,0]:.2f},{pts[k,1]:.2f},{x1[k]:.2f},{y1[k]:.2f}")

with open("tracks.csv", "w") as f:
    f.write("\n".join(lines) + "\n")
with open("meta.json", "w") as f:
    json.dump({"num_frames": len(params) + 1}, f)

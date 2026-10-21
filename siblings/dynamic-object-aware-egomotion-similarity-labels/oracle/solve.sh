#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_ego.py << 'EOF'
import json, math
import numpy as np

n = json.load(open("meta.json"))["num_frames"]
data = np.loadtxt("tracks.csv", delimiter=",", skiprows=1)
labels = []
for i in range(n - 1):
    r = data[data[:, 0] == i]
    M, y = [], []
    for _, x0, y0, x1, y1 in r:
        M.append([x0, -y0, 1, 0]); y.append(x1)
        M.append([y0, x0, 0, 1]); y.append(y1)
    a, b, tx, ty = np.linalg.lstsq(np.array(M), np.array(y), rcond=None)[0]
    s = math.hypot(a, b)
    rot = math.atan2(b, a)
    lab = []
    if abs(s - 1) > 0.02:
        lab.append("Dolly In" if s > 1 else "Dolly Out")
    if abs(rot) > 0.01:
        lab.append("Roll Right" if rot > 0 else "Roll Left")
    if abs(tx) > 2 and abs(tx) >= abs(ty):
        lab.append("Pan Left" if tx > 0 else "Pan Right")
    if abs(ty) > 2 and abs(ty) > abs(tx):
        lab.append("Tilt Up" if ty > 0 else "Tilt Down")
    labels.append(lab if lab else ["Stay"])
labels.append(labels[-1])

out = {}
start = 0
for f in range(1, n + 1):
    if f == n or set(labels[f]) != set(labels[start]):
        out[f"{start}->{f}"] = labels[start]
        start = f
json.dump(out, open("pred_instructions.json", "w"), indent=2)
EOF
python3 /tmp/solve_ego.py

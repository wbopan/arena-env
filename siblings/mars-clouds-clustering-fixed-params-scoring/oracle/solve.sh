#!/bin/bash
set -e
cat > /tmp/solve.py << 'EOF'
import json
import numpy as np
import pandas as pd

EPS, MS, W = 10.0, 4, 1.4
cit = pd.read_csv("/root/work/citsci.csv")
exp = pd.read_csv("/root/work/expert.csv")


def dbscan(P):
    n = len(P)
    dx = P[:, 0][:, None] - P[:, 0][None, :]
    dy = P[:, 1][:, None] - P[:, 1][None, :]
    D = np.sqrt((W * dx) ** 2 + ((2 - W) * dy) ** 2)
    N = D <= EPS
    core = N.sum(1) >= MS
    lab = -np.ones(n, int)
    cid = 0
    for i in range(n):
        if core[i] and lab[i] < 0:
            stack = [i]
            lab[i] = cid
            while stack:
                j = stack.pop()
                for k in np.where(N[j] & core)[0]:
                    if lab[k] < 0:
                        lab[k] = cid
                        stack.append(k)
            cid += 1
    out = lab.copy()
    for i in range(n):
        if not core[i]:
            c = np.where(N[i] & core)[0]
            if len(c):
                out[i] = lab[c[np.argmin(D[i, c])]]
    return out


images = {}
for name in sorted(exp.file_rad.unique()):
    E = exp[exp.file_rad == name][["x", "y"]].to_numpy(float)
    P = cit[cit.file_rad == name][["x", "y"]].to_numpy(float)
    cents = []
    if len(P):
        lab = dbscan(P)
        for c in sorted(set(lab.tolist()) - {-1}):
            cents.append(P[lab == c].mean(0))
    C = np.array(cents).reshape(-1, 2)
    pairs = sorted((float(np.hypot(*(C[a] - E[b]))), a, b) for a in range(len(C)) for b in range(len(E)))
    ua, ub, d = set(), set(), []
    for dist, a, b in pairs:
        if dist > 100:
            break
        if a in ua or b in ub:
            continue
        ua.add(a); ub.add(b); d.append(dist)
    m = len(d)
    images[name] = {
        "n_clusters": int(len(C)),
        "n_matched": m,
        "F1": round(2 * m / (len(C) + len(E)), 4) if m else 0.0,
        "delta": round(float(np.mean(d)), 4) if m else None,
    }

raw_f1 = []
raw_d = []
for name in images:
    raw_f1.append(images[name]["F1"])
    if images[name]["delta"] is not None:
        raw_d.append(images[name]["delta"])
res = {"images": images, "mean_F1": round(float(np.mean(raw_f1)), 4), "mean_delta": round(float(np.mean(raw_d)), 4)}
with open("/root/work/image_scores.json", "w") as f:
    json.dump(res, f, indent=2)
EOF
python3 /tmp/solve.py

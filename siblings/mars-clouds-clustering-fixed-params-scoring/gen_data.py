import numpy as np
import pandas as pd

rng = np.random.default_rng(20240611)
expert, cit = [], []
for i in range(10):
    name = f"orbit{3100 + 7 * i}_rad"
    k = int(rng.integers(3, 7))
    centers = []
    while len(centers) < k:
        c = rng.uniform(40, 460, 2)
        if all(np.hypot(*(c - d)) > 70 for d in centers):
            centers.append(c)
    for c in centers:
        expert.append((name, round(float(c[0]), 2), round(float(c[1]), 2)))
    if i in (3, 8):
        continue
    for c in centers:
        n = int(rng.integers(2, 10))
        off = rng.normal(0, 4, 2)
        for _ in range(n):
            x = c[0] + off[0] + rng.normal(0, 2.5)
            y = c[1] + off[1] + rng.normal(0, 7.0)
            cit.append((name, round(float(x), 2), round(float(y), 2)))
    if rng.random() < 0.5:
        s = rng.uniform(40, 460, 2)
        for _ in range(int(rng.integers(4, 7))):
            cit.append((name, round(float(s[0] + rng.normal(0, 2.5)), 2), round(float(s[1] + rng.normal(0, 6.0)), 2)))
    for _ in range(int(rng.integers(3, 7))):
        cit.append((name, round(float(rng.uniform(0, 500)), 2), round(float(rng.uniform(0, 500)), 2)))

order = rng.permutation(len(cit))
cit = [cit[j] for j in order]
pd.DataFrame(expert, columns=["file_rad", "x", "y"]).to_csv("expert.csv", index=False)
pd.DataFrame(cit, columns=["file_rad", "x", "y"]).to_csv("citsci.csv", index=False)

#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_transit.py <<'EOF'
import json
import numpy as np

d = np.loadtxt('tess_lc.txt', comments='#')
d = d[d[:, 2] == 0]
d = d[np.argsort(d[:, 0])]
t = d[:, 0]
f = d[:, 1]
t_first = t[0]
trend = np.empty_like(f)
for i in range(len(t)):
    trend[i] = np.median(f[np.abs(t - t[i]) <= 0.5])
y = f / trend
res = y - np.median(y)
mad = 1.4826 * np.median(np.abs(res))
keep = res < 5 * mad
t = t[keep]
y = y[keep]
dy = y - y.mean()
n = len(y)
nb = 240
durs = [0.0625, 0.09, 0.12, 0.15, 0.18, 0.2]
bestv, bestP, bestd = -1.0, None, None
for P in np.arange(1.0, 5.0, 0.0004):
    b = np.minimum((((t - t[0]) / P) % 1.0 * nb).astype(int), nb - 1)
    s = np.bincount(b, weights=dy, minlength=nb)
    c = np.bincount(b, minlength=nb).astype(float)
    s2 = np.concatenate([[0.0], np.cumsum(np.tile(s, 2))])
    c2 = np.concatenate([[0.0], np.cumsum(np.tile(c, 2))])
    for du in durs:
        k = max(1, int(round(du / P * nb)))
        S = s2[k:k + nb] - s2[:nb]
        R = (c2[k:k + nb] - c2[:nb]) / n
        ok = (R > 0) & (R < 1) & (S < 0)
        if not ok.any():
            continue
        v = (S[ok] ** 2 / (R[ok] * (1 - R[ok]))).max()
        if v > bestv:
            bestv, bestP, bestd = v, P, du
P, du = bestP, bestd
bv, bt0, bm = -1.0, None, None
for t0 in t_first + np.arange(0.0, P, 0.002):
    ph = (t - t0 + 0.5 * P) % P - 0.5 * P
    m = np.abs(ph) < 0.5 * du
    if m.sum() == 0 or m.all():
        continue
    S = dy[m].sum()
    if S >= 0:
        continue
    R = m.mean()
    v = S ** 2 / (R * (1 - R))
    if v > bv:
        bv, bt0, bm = v, t0, m
depth = (y[~bm].mean() - y[bm].mean()) * 1000.0
with open('transit.json', 'w') as fh:
    json.dump({'period_days': round(float(P), 5), 't0': round(float(bt0), 5), 'depth_ppt': round(float(depth), 3)}, fh)
EOF
python3 /tmp/solve_transit.py

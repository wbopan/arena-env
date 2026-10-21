#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_lin.py <<'EOF'
import json
import numpy as np

c = json.load(open("system_config.json"))
n = c["n_sections"]
EA, R, fb, dt = c["EA"], c["R"], c["fb"], c["dt"]
L, J, T = c["L"], c["J"], c["T_ref"]

v = []
vp, Tp = c["v0"], 0.0
for i in range(n):
    vi = vp * (EA - Tp) / (EA - T[i])
    v.append(vi)
    vp, Tp = vi, T[i]

u = []
for i in range(n):
    Tn = T[i + 1] if i < n - 1 else 0.0
    u.append((fb * v[i] - R * R * (Tn - T[i])) / R)

A = np.zeros((2 * n, 2 * n))
B = np.zeros((2 * n, n))
for i in range(n):
    A[i, i] = -v[i] / L[i]
    A[i, n + i] = (EA - T[i]) / L[i]
    if i > 0:
        A[i, i - 1] = v[i - 1] / L[i]
        A[i, n + i - 1] = (T[i - 1] - EA) / L[i]
    A[n + i, i] = -R * R / J[i]
    A[n + i, n + i] = -fb / J[i]
    if i < n - 1:
        A[n + i, i + 1] = R * R / J[i]
    B[n + i, i] = R / J[i]

Ad = np.eye(2 * n) + dt * A
Bd = dt * B
rho = float(np.max(np.abs(np.linalg.eigvals(Ad))))

json.dump({
    "v_ref": v,
    "u_ref": u,
    "A_matrix": Ad.tolist(),
    "B_matrix": Bd.tolist(),
    "spectral_radius": rho,
}, open("linearization.json", "w"), indent=2)
EOF
python3 /tmp/solve_lin.py

import json

import numpy as np

rng = np.random.default_rng(11)
n = 3
EA = rng.uniform(900, 1400)
R = rng.uniform(0.08, 0.12)
fb = rng.uniform(0.005, 0.02)
dt = 0.01
v0 = rng.uniform(0.5, 1.5)
L = rng.uniform(0.6, 1.4, n)
J = rng.uniform(0.03, 0.08, n)
T = rng.integers(15, 45, n).astype(float)

v = np.zeros(n)
vp, Tp = v0, 0.0
for i in range(n):
    v[i] = vp * (EA - Tp) / (EA - T[i])
    vp, Tp = v[i], T[i]

Ac = np.zeros((2 * n, 2 * n))
Bc = np.zeros((2 * n, n))
for i in range(n):
    Ac[i, i] = -v[i] / L[i]
    Ac[i, n + i] = (EA - T[i]) / L[i]
    if i > 0:
        Ac[i, i - 1] = v[i - 1] / L[i]
        Ac[i, n + i - 1] = (T[i - 1] - EA) / L[i]
    Ac[n + i, i] = -R ** 2 / J[i]
    Ac[n + i, n + i] = -fb / J[i]
    if i < n - 1:
        Ac[n + i, i + 1] = R ** 2 / J[i]
    Bc[n + i, i] = R / J[i]

A = np.eye(2 * n) + dt * Ac
B = dt * Bc
np.savetxt("A.csv", A, delimiter=",", fmt="%.12e")
np.savetxt("B.csv", B, delimiter=",", fmt="%.12e")
A = np.loadtxt("A.csv", delimiter=",")
B = np.loadtxt("B.csv", delimiter=",")

Q = [1.0] * n + [0.1] * n
Rd = [0.05] * n
N = 10
x0 = [round(float(t), 3) for t in rng.uniform(-8, 8, n)] + [0.0] * n

# Pick a torque limit that makes the initial input saturate.
Qm = np.diag(Q)
Rm = np.diag(Rd)
P = Qm.copy()
for _ in range(N):
    K = np.linalg.solve(Rm + B.T @ P @ B, B.T @ P @ A)
    P = Qm + A.T @ P @ (A - B @ K)
u0 = -K @ np.array(x0)
u_max = round(0.5 * float(np.max(np.abs(u0))), 4)

cfg = {
    "horizon_N": N,
    "Q_diag": Q,
    "R_diag": Rd,
    "x0": x0,
    "u_max": u_max,
    "steps": 150,
}
with open("mpc_config.json", "w") as f:
    json.dump(cfg, f, indent=2)

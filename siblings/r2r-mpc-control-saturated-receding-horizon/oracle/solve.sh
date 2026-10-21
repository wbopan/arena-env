#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_mpc.py <<'EOF'
import json
import numpy as np

A = np.loadtxt("A.csv", delimiter=",")
B = np.loadtxt("B.csv", delimiter=",")
c = json.load(open("mpc_config.json"))
Q = np.diag(c["Q_diag"])
R = np.diag(c["R_diag"])

# Backward Riccati recursion with terminal cost P_N = Q.
P = Q.copy()
for _ in range(c["horizon_N"]):
    K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
    P = Q + A.T @ P @ (A - B @ K)

x = np.array(c["x0"], float)
lines = ["k,x_norm,u1,u2,u3"]
for k in range(c["steps"]):
    u = np.clip(-K @ x, -c["u_max"], c["u_max"])
    lines.append(f"{k},{np.linalg.norm(x):.6f},{u[0]:.6f},{u[1]:.6f},{u[2]:.6f}")
    x = A @ x + B @ u
open("closed_loop.csv", "w").write("\n".join(lines) + "\n")
EOF
python3 /tmp/solve_mpc.py

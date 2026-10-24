## Reference notes

Use `numpy` for the Riccati recursion and simulation, `json` for configuration, and the standard-library `csv` module for output. `A.csv` and `B.csv` have **no headers**: load with `np.loadtxt(path, delimiter=",")`. Build `Q = np.diag(config["Q_diag"])` and `R = np.diag(config["R_diag"])`; the matrices are already discrete, so do not linearize or discretize them again.

For the specified terminal cost, initialize \(P_N=Q\). Work backward from \(j=N-1\) to \(0\):

```python
P = Q.copy()
for j in range(N - 1, -1, -1):
    K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
    P = Q + A.T @ P @ (A - B @ K)
    if j == 0:
        K0 = K.copy()
```

At every simulation step, the unconstrained first-horizon input is `-K0 @ x`. Clip **that input** with `np.clip(u, -u_max, u_max)` before recording it or updating the plant. Because `A`, `B`, `Q`, `R`, and `N` are fixed, `K0` can be computed once; receding-horizon control still evaluates it at the current state each step. Clipping does not change the Riccati recursion.

Record `np.linalg.norm(x)` **before** updating `x = A @ x + B @ u`. Write one CSV row per step with header `k,x_norm,u1,u2,u3`; format floating-point fields to six decimal places (for example, `f"{value:.6f}"`). No integral action or additional terminal-cost calculation is called for.

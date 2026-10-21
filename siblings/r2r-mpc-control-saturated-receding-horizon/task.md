# Receding-Horizon LQR Tension Regulation with Torque Limits

A 3-section roll-to-roll line has already been linearized and discretized. The inputs are in `/root/work`:

- `A.csv`: the 6x6 discrete state matrix. Comma-separated, no header.
- `B.csv`: the 6x3 discrete input matrix. Comma-separated, no header.
- `mpc_config.json`: contains `horizon_N`, `Q_diag` (6 values), `R_diag` (3 values), `x0` (6 values), `u_max`, and `steps`.

The state x is the deviation from the operating point, ordered as [T1, T2, T3, v1, v2, v3]. The input u is the torque deviation.

The controller works as follows. At every step k, it solves the finite-horizon LQR problem from the current state x_k. The cost is the sum over j = 0..N-1 of (x_j' Q x_j + u_j' R u_j), plus a terminal cost x_N' Q x_N, where Q = diag(Q_diag), R = diag(R_diag) and N = `horizon_N`. The controller applies only the first optimal input, clipped elementwise to [-u_max, u_max].

The plant evolves as x_{k+1} = A x_k + B u_k, where u_k is the clipped input. Simulate from x_0 = `x0` for k = 0 .. steps-1.

Write `/root/work/closed_loop.csv` with these specifications:

- Header: `k,x_norm,u1,u2,u3`
- One row per step, k = 0 .. steps-1.
- `x_norm` is the Euclidean norm of x_k, the state before the input at step k is applied.
- `u1..u3` are the applied, clipped inputs at step k.
- Round all values to 6 decimals.

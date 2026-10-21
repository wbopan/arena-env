1. Grep `r2r_simulator.py` for its class, step API and dynamics, and print `system_config.json` truncated to get dt, EA, L, J, R, T_ref, v_ref and the step definition.
2. Write one script that builds discrete A and B at the initial reference by Jacobian/finite differences plus discretization, then gets P from `solve_discrete_are` and K_0 from the finite-horizon Riccati recursion (N≈10, Q=100/T²,0.1/v², R≈0.033).
3. Run u = u_ref(t) − K_0(x − x_ref(t)) + a leaky integral term for at least 5 s, logging time, tensions, velocities, inputs and 12 references.
4. Write `controller_params.json`, `control_log.json` (phase "control") and `metrics.json` (SSE, settling time after t=0.5, max and min tension).
5. Reload each file to check shapes, check SSE < 2, settling < 4, max < 50 and min > 5, then retune R or c_I if needed.

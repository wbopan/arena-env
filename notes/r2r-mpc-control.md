**Goal.** Write one Python script that does four things:
1. Linearizes the simulator dynamics at the initial reference point.
2. Designs an MPC controller, implemented as finite-horizon LQR with a DARE terminal cost.
3. Runs the controller through the unmodified `r2r_simulator.py` for at least 5 s.
4. Writes `controller_params.json`, `control_log.json` and `metrics.json` in the working directory, or wherever the task or tests expect them. Check for an output dir mentioned in the simulator, config or tests.

**1. Inspect inputs cheaply (do not cat whole files)**
- `ls; wc -l r2r_simulator.py system_config.json`
- `python -c "import json;print(json.dumps(json.load(open('system_config.json')),indent=1)[:1500])"`. Look for EA, L, J, R (roller radius), friction, dt, T_ref, v_ref, initial state, torque limits, and the step definition (section 3, 20→44 N at t=0.5).
- `grep -n "def \|class \|return\|dt\|EA\|step\|ref" r2r_simulator.py | head -60`. Find:
  - the class name and constructor arguments;
  - `reset`/`step(u)` signatures and their return values (state, time);
  - whether a dynamics function f(x,u) is exposed;
  - how the reference changes over time (it may be a method like `get_reference(t)`).
- Then `sed -n 'a,bp'` only the dynamics function to read the exact tension and velocity equations, including signs, coupling to neighbouring sections, and friction.

**2. Model**
- State is x = [T1..T6, v1..v6] (12 states) and input is u = [u1..u6] (6 inputs).
- A typical web form is
  - dT_i/dt = (EA/L)(v_i − v_{i−1}) + (v_{i−1}T_{i−1} − v_i T_i)/L
  - dv_i/dt = (R²/J)(T_{i+1} − T_i) + (R/J)u_i − friction.
- Always use the simulator's exact equations. The skill partials are ∂Ṫ_i/∂T_i = −v_i/L, ∂Ṫ_i/∂v_i = EA/L − T_i/L, ∂v̇_i/∂T_i = −R²/J and ∂v̇_i/∂u_i = R/J. These include the neighbour terms implied by the equations.

**Get A and B robustly.**
- If the simulator exposes f(x,u), take central finite differences at (x_ref0, u_ref0) with eps ≈ 1e-6·max(1,|x|).
- Otherwise code the analytic Jacobian from the equations you read.
- x_ref0 is the INITIAL reference (T_ref from config, before the step).
- Find the steady-state torque u_ref by solving f(x_ref, u) = 0 for u. The velocity equations are linear in u, so u_ref = pinv(B_c[6:,:]) @ (−f_v(x_ref, 0)), or use `scipy.optimize.least_squares`.

**Discretize with the simulator dt.**
- Euler: A = I + dt·A_c, B = dt·B_c.
- Or exact: `scipy.linalg.expm` of the block matrix [[A_c, B_c], [0, 0]]·dt.
- These discrete A (12×12) and B (12×6) are what you save.
- Check `np.abs(np.linalg.eigvals(A))`.

**3. Controller**
- Weights from the skill:
  - Q = diag([100/T_ref_i²]*6 + [0.1/v_ref_i²]*6). Plain 100 and 0.1 are also acceptable, as in the example. All entries must be positive.
  - R = 0.01–0.1·I, e.g. 0.033.
  - N in [3, 30]; 5–15 is typical, e.g. 10.
- Terminal cost and infinite-horizon gain:
  - `P = scipy.linalg.solve_discrete_are(A, B, Q, R)`
  - `K_lqr = np.linalg.solve(R + B.T@P@B, B.T@P@A)`. This is 6×12.
- MPC backward Riccati, starting from P_N = P:
  - for k = N−1…0: K_k = solve(R + BᵀPB, BᵀPA), then P = Q + AᵀP(A − BK_k).
  - Apply the first gain K_0.
  - The model is LTI, so K_0 can be computed once. It equals K_lqr when P_N = DARE.
- Control law at each step:
  - Read x and the current reference x_ref(t) from the simulator. T3_ref becomes 44 at t = 0.5.
  - Recompute u_ref for the current reference whenever it changes.
  - u = u_ref − K_0(x − x_ref) + u_I.
- Integral action per section i: u_I[i] = γ·u_I[i] − c_I·dt·(T_i − T_ref_i), with γ ≈ 0.95–0.99 and c_I ≈ 0.1–0.5. Clip u_I for anti-windup.
- Verify the sign: increasing u_i must raise T_i in this simulator. Check the sign of B_c entries via the T-row of A_c times B. If the sign is opposite, flip it.
- Clip u to the simulator torque limits if they exist.

**4. Simulation and log**
- Run for at least 5 s: steps = ceil(5.0/dt) + a few.
- For each step, append `{"time": t, "tensions": [6 floats], "velocities": [6 floats], "control_inputs": [6 floats], "references": [12 floats: T1..T6_ref, v1..v6_ref]}`.
- Convert numpy types with `float()`.
- Save as `{"phase": "control", "data": [...]}`. The last time minus the first time must be ≥ 5 s, so start time near 0 or dt.

**5. Metrics (`metrics.json`, keys exactly as below)**
- `steady_state_error`: mean of |T − T_ref| over all 6 sections for the final portion, e.g. the last 1–2 s. T_ref is the config reference with the stepped section-3 value after t = 0.5. Target < 2.0.
- `settling_time`: time after the step at t = 0.5 until all tensions stay within a tolerance band (e.g. 5% of ref or ±2 N) for the rest of the run. Report it relative to the step (t_settle − 0.5), or absolute if that convention appears in config or tests. Target < 4.0.
- `max_tension`: max over all logged tensions. Target < 50.
- `min_tension`: min over all logged tensions. Target > 5.
- If a test file exists (`ls tests/ 2>/dev/null; grep -rn settling` in tests), match its definitions.

**6. `controller_params.json`**
- `{"horizon_N": int, "Q_diag": 12 floats, "R_diag": 6 floats, "K_lqr": 6×12, "A_matrix": 12×12, "B_matrix": 12×6}`.
- Use `.tolist()` for the matrices.
- A and B must be the discrete matrices linearized at the initial reference.

**Pitfalls**
- Do not edit `r2r_simulator.py`. Import it.
- Don't print the whole log. Print only the metrics and `len(data)`.
- If the response overshoots past 50 N or oscillates, raise R, lower c_I, or reduce the Q tension weight.
- If steady-state error stays above 2, increase c_I or check that u_ref is recomputed after the step.
- Verify the output files afterwards: load each JSON, check shapes (`np.array(...).shape`), check the time span, and check all values are finite.

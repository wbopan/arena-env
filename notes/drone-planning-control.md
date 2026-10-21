**Inputs to inspect cheaply**
- `ls /root/commands; head -n 3 /root/commands/*.txt`. Each file holds one command line.
- `cat /root/system_params.yaml`. It is small. Note the exact key names: mass, gravity, inertia, arm length `d`, `cT`, `cQ`, `rpm_min`/`rpm_max`, motor constant `km`, `sample_rate`, `accel_limit_up/down/horiz`. Load it with `yaml.safe_load`.
- Use `dt = 1/sample_rate`. Never hardcode 0.005.

**Parser** (regex, `re.IGNORECASE`, one pattern per type)
- `take\s*off to ([\d.]+) m height in ([\d.]+) sec` → takeoff, from z=0 to z=h.
- `hover at ([\d.]+) m height for ([\d.]+) sec` → hover. Start and end are both (0,0,h).
- `land from ([\d.]+) m height in ([\d.]+) sec` → land, from h to 0.
- `fly from \(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\) to \(...\) in ([\d.]+) sec` → fly. Seven groups.
- Output: `waypoints` (4×2: x, y, z, yaw=0), `times=[0,T]`, `modes=[mode]`.
- Pitfall: the skill auto-inserts start (0,0,0). For hover, land and fly, insert the start the command implies (h, or the "from" point). Otherwise the drone starts far from the plan.

**Trajectory planner** → (15 × max_iter)
- `max_iter = int(round(T*sample_rate)) + 1`.
- Do NOT use `CubicSpline` with only 2 points. It degenerates to a straight line with nonzero velocity at t=0, which gives an instant tracking error. Use `CubicSpline(times, pts, bc_type='clamped')` (zero end velocities) or a quintic min-jerk curve.
- Min-jerk formula: `s=τ³(10−15τ+6τ²)`, `ṡ=30τ²(1−τ)²/T`, `s̈=60τ(1−2τ+... )/T²`. Here `s̈ = (60τ−180τ²+120τ³)/T²`, and its peak is 5.77·Δ/T².
- Rows: 0:3 pos, 3:6 vel, 12:15 acc.
- Hover: constant pos, zero vel and acc.
- Rows 6:9 hold [φ_des, θ_des, ψ] from the attitude planner applied to the planned acc. Rows 9:12 are 0.
- Check before saving:
  - `acc[2].max() <= accel_limit_up`
  - `acc[2].min() >= -accel_limit_down` (check the sign convention in the yaml)
  - `hypot(ax, ay).max() <= accel_limit_horiz`
- Peak acceleration is 6Δ/T² (clamped cubic) or 5.77Δ/T² (quintic). With short times, verify these.

**Motor model**
- Allocation rows:
  - `[cT,cT,cT,cT]`
  - `[0,d·cT,0,−d·cT]`
  - `[−d·cT,0,d·cT,0]`
  - `[−cQ,cQ,−cQ,cQ]`
- `rpm_des = clip(sqrt(max(solve(P,[F,M]),0)), rpm_min, rpm_max)`.
- `rpm_dot = km*(rpm_des − rpm)`.
- Actual forces: `[F_a, M_a] = P @ rpm**2`.
- Initialise the rpm state at hover: `sqrt(m g /(4 cT))`.

**Dynamics** (state 16: pos, vel, euler, omega, rpm)
- `ẍ = F/m (cosφ sinθ cosψ + sinφ sinψ)`
- `ÿ = F/m (cosφ sinθ sinψ − sinφ cosψ)`
- `z̈ = −g + F/m cosφ cosθ`
- Euler rate = ω.
- `ω̇ = solve(I, M)`.
- `rpm̄̇ = rpm_dot`.
- Integrate each step with `solve_ivp(f,[0,dt],s,method='RK45')` and take `sol.y[:,-1]`. F and M are held constant during the step.
- Actual-state rows 12:15 are the translational acceleration evaluated from the dynamics (or the finite-difference of velocity).
- Initial actual state = planned state at k=0 (pos, zero vel) with hover rpm.

**Controllers** (integrals are fresh dicts `{"e":zeros(3)}` per run; no mutable defaults)
- Position controller:
  - `e=pos−pos_des`, `ev=vel−vel_des`, `I+=e*dt`
  - `acc = acc_des − kp*e − ki*I − kd*ev`
  - `F = m*(g+acc[2])`
- Attitude planner:
  - `φ_des=(ax sinψ − ay cosψ)/g`
  - `θ_des=(ax cosψ + ay sinψ)/g`
  - `ω_des=[0,0,0]`
- Attitude controller:
  - `e=rot_des−rot`, `Ia+=e*dt`
  - `M = I_mat @ (kp_att*e + ki_att*Ia + kd_att*(ω_des−ω))`. Gains multiply element-wise.
- Keep ki small: ki_att ≤ 0.5, ki_pos small or 0. Feed-forward `acc_des` is what keeps tracking error tiny.
- Plausible search region:
  - kp_pos 5–30, kd_pos 3–10
  - kp_att 100–2000, kd_att 10–60
- Remember the motor lag τ≈27 ms. Very high attitude gains oscillate.

**Tuning**
- Run a small grid (e.g. 10–30 combos, time-limited) per command.
- Score:
  - must have `max ||pos_act−pos_des|| < 0.05` at every k
  - must have SSE < 0.05 and Overshoot < 5
  - among passing runs, minimise max error
- Keep the best gains as lists of 3 floats.

**Metrics** (stepinfo_3d, threshold 0.02)
- `target = waypoints[0:3,-1]`, `dist = ||pos−target||`, `d0 = dist[0]`.
- If `d0 < 1e-6`, all metrics are 0 (hover).
- RiseTime = first t with `dist ≤ 0.1 d0`.
- SettlingTime = last t with `dist > 0.02 d0`.
- Overshoot = max dist after first entering the band, `/d0*100`. It is 0 if the band is never entered.
- SSE = `dist[-1]`.
- Cast every value to Python `float`.

**Outputs** (per command label = filename stem, e.g. `001`), in `/root/results/<label>/`:
- `metrics_3d.json`: `{"mode": mode, "RiseTime":…, "SettlingTime":…, "Overshoot_pct":…, "SteadyStateError":…}`
- `tuning_results.json`: keys `kp_pos, ki_pos, kd_pos, kp_att, ki_att, kd_att`, each a list of 3 floats.
- `planned_trajectory.npy`: shape (15, max_iter).
- `actual_trajectory.npy`: shape (15, max_iter), same length as the planned file.
- `plots/desired_vs_actual.png`, `plots/errors.png`, `plots/cumulative_errors.png`:
  - Use `matplotlib.use('Agg')`, 5×3 subplots, `figsize=(16,20)`.
  - Desired in blue, actual in red.
  - errors = actual−desired; cumulative = `dt*cumsum(|err|)`.
  - `os.makedirs(...,exist_ok=True)`, `savefig`, `plt.close`.

**Plan**
1. Inspect the yaml and commands (2–3 commands).
2. Write `/root/sim.py` in one heredoc containing everything above, plus a loop over `sorted(glob('/root/commands/*.txt'))`.
3. Run `python3 /root/sim.py`. Print only one summary line per command: mode, max err, SSE, OS, max |az|, max horiz acc.
4. If any command fails, adjust the gain grid or switch to the smoother quintic profile, then rerun.
5. Verify with a one-liner:
   - npy shapes match and are (15, N)
   - JSON keys are present
   - all three PNGs exist
   - error < 0.05 at every timestep, recomputed from the saved npy files
   - acceleration limits hold on the saved planned file

**Goal and outputs.** Write five JSON files in the working directory (the same directory as `hvac_simulator.py`, unless the task or tests say otherwise). Use exactly these keys:

- `calibration_log.json`: `{"phase":"calibration","heater_power_test":<float>,"data":[{"time","temperature","heater_power"},...]}`. It needs at least 30 s of data and at least 20 points.
- `estimated_params.json`: `{"K","tau","r_squared","fitting_error"}`.
- `tuned_gains.json`: `{"Kp","Ki","Kd","lambda"}`.
- `control_log.json`: `{"phase":"control","setpoint":22.0,"data":[{"time","temperature","setpoint","heater_power","error"},...]}`. It must span at least 150 s of control.
- `metrics.json`: `{"rise_time","overshoot","settling_time","steady_state_error","max_temp"}`. Overshoot is a fraction (0.05 means 5%).

**Targets.**
- Steady-state error < 0.5 °C.
- Settling time < 120 s.
- Overshoot < 0.10.
- max_temp < 30 °C.
- Heater power clamped to 0–100.

Cast every value to a plain Python `float` (no numpy types) before `json.dump`.

**Step 1: Inspect the simulator cheaply. Do not cat whole files.**
- `wc -l hvac_simulator.py; grep -n "def \|class \|dt\|noise\|ambient\|max\|json\|yaml\|open(" hvac_simulator.py | head -60`
- `ls` to spot any config file (yaml/json) the simulator reads.
- Find out:
  - the class name and constructor arguments;
  - how to read the initial temperature;
  - the step method signature, e.g. `step(heater_power)`, and what it returns (dict keys such as time/temperature/heater_power);
  - the time step `dt`;
  - whether there is a `reset()`;
  - any built-in safety cutoff.
- If the simulator writes logs itself, note the file names it uses.

**Step 2: Calibration (open-loop step test).**
1. Record t=0 with heater 0 and the initial temperature.
2. Apply a moderate constant step, `heater_power_test = 50.0`.
3. Log every sample.
4. Duration: the skills recommend 3–5 time constants (at least 2–3) and 10–20 samples per tau. If tau is unknown, run about 60–120 s of simulated time, which gives far more than 20 points.
5. Safety: if the temperature reaches the limit (e.g. ≥ 28 °C, keeping margin below 30), set power to 0.

**Step 3: Fit a first-order model with `scipy.optimize.curve_fit`.**
- The model is `y(t) = y0 + K*u*(1-exp(-(t-t0)/tau))`.
  - `u` is the known step (50).
  - `y0` is fixed to the initial reading; average the first few pre-step readings if noisy.
  - Use only points from the step onset `t0`.
- Initial guesses:
  - `K0 = (y[-1]-y0)/u`.
  - `tau0` = time to reach 63.2 % of the rise, or `t[len//3]`.
- Bounds: `([1e-6, 0.1], [10, 1e4])`.
- Quality metrics:
  - `r2 = 1 - SSres/SStot`; aim for > 0.9.
  - `fitting_error = sqrt(mean(res**2))`.
- Do not smooth the data heavily. The fit averages out noise.
- A low R² means the data missed the transient or the step onset was wrong.

**Step 4: IMC PI tuning.**
- Formulas:
  - `Kp = tau/(K*lam)`
  - `Ki = Kp/tau = 1/(K*lam)`
  - `Kd = 0`
- Keep the saved gains exactly consistent with the saved K and tau. Tests may recompute them.
- Choosing `lam`:
  - Expected settling time is about 4·λ and rise time about 2.2·λ. Settling must be < 120 s, so pick λ around 20–30 s (e.g. `lam = min(tau, 25)`).
  - If tau is already small, `lam = tau` is fine.
  - Larger λ is more robust to noise.
- Save `"lambda": lam`.

**Step 5: Closed loop.**
- Starting point:
  - If the simulator has `reset()` (or you can re-instantiate it), start control from the cool initial state.
  - Otherwise continue from the end of calibration. The example log starts at t=30, i.e. sim time continues.
  - If calibration left the room above about 21 °C, wait at 0 % or reset first. Otherwise the controller starts near or above the setpoint and overshoot/settling are ill-defined.
- Each step:
  - `e = 22 - T`
  - `integral += e*dt`
  - `u = Kp*e + Ki*integral`, then clamp to 0–100.
  - Anti-windup: only integrate when not saturated, or undo the increment if clamped.
  - Safety first: if `T >= 28`, set `u = 0`.
- Log time, temperature, setpoint, heater_power and error at every step.
- Run at least 150 s; 180–200 s gives margin.

**Step 6: Metrics, computed from control_log data, with time relative to control start.**
- `T0` = first temperature; `step = 22 - T0`.
- `rise_time`: time from 10 % to 90 % of the step, or the first time reaching 90 %.
- `max_temp = max(T)`.
- `overshoot = max(0, (max_temp-22)/step)`, as a fraction.
- `settling_time`: the last time |T-22| was outside the band, relative to control start. Use a ±0.5 °C band (or ±2 % of step, if larger, to tolerate noise). It is 0 if never outside.
- `steady_state_error`: mean |22 - T| over the last ~20–30 % of the log.
- Sensor noise can make single samples leave the band. Compute settling on a short moving average only if needed.

**Step 7: Evaluate and verify.**
- Print a compact summary:
  - `python -c "import json;[print(f,json.load(open(f)) if f!='control_log.json' and f!='calibration_log.json' else len(json.load(open(f))['data'])) for f in [...]]"`
- Check point counts, durations (calibration ≥ 30 s, control ≥ 150 s), r² > 0.9, overshoot < 0.1, settling < 120, sse < 0.5, max_temp < 30.
- If any metric fails, adjust λ: increase it for overshoot or oscillation, decrease it for slow settling. Then regenerate tuned_gains.json and re-run control so all files stay consistent.
- If the simulator has its own logging or evaluation helpers, run them.

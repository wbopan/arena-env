**Files to produce (all in the working directory, next to `vehicle_params.yaml` and `sensor_data.csv`):**
- `pid_controller.py`
- `acc_system.py`
- `simulation.py`
- `tuning_results.yaml`
- `simulation_results.csv`
- `acc_report.md`

**1. Inspect the inputs cheaply. Never print whole files.**
- `cat vehicle_params.yaml`. It is small; learn the exact key names, e.g. `config['acc_settings']['set_speed']`, plus the names for time headway, min gap, TTC threshold and accel limits.
- `head -5 sensor_data.csv; wc -l sensor_data.csv`. Expect a header plus 1501 rows.
- `python3 -c "import pandas as pd;d=pd.read_csv('sensor_data.csv');print(d.isnull().sum());print(d[d.lead_speed.notna()].time.agg(['min','max']))"`. This shows where a lead vehicle exists. NaN `lead_speed`/`distance` means no lead, which is cruise mode.
- Read the CSV with `pd.read_csv(path, na_values=['','NA','null'])` and test each value with `pd.isna(v)`.

**2. pid_controller.py**

The class is `PIDController(kp, ki, kd)`, with optional `output_min/output_max` and `integral_limit` kwargs. It has `reset()` and `compute(error, dt) -> float`. The discrete law is:

```python
self.integral += error*dt
# clamp the integral (anti-windup), e.g. to ±integral_limit
deriv = (error - self.prev_error)/dt if dt > 0 else 0.0
self.prev_error = error
out = kp*error + ki*self.integral + kd*deriv
# clamp out if limits are given
return float(out)
```

- `reset()` sets the integral and `prev_error` to 0.
- Anti-windup options are integral clamping or conditional integration (skip integrating when saturated). This matters because the start is saturated at +3 m/s² for about 10 s.
- Tip: on the first call, set `prev_error = error` so there is no derivative kick.

**3. acc_system.py**

The class is `AdaptiveCruiseControl(config)`, where `config` is the nested dict from `yaml.safe_load`.
- Read the limits, `set_speed` (30), `time_headway` (1.5), `min_distance` (10) and `ttc_threshold` (3.0) from the config.
- Create two PIDs, `pid_speed` and `pid_distance`. Their gains come from `config['pid_speed']` and `config['pid_distance']` if present; otherwise pass them as an argument or attribute.

`compute(ego_speed, lead_speed, distance, dt)` returns `(acceleration_cmd, mode, distance_error)`:
- **Cruise** (`lead_speed is None`, or distance is None/NaN):
  - `acc = pid_speed.compute(set_speed - ego_speed, dt)`
  - `mode = 'cruise'`, `distance_error = None`
- **Otherwise**, compute:
  - `desired = ego_speed*time_headway + min_distance`
  - `distance_error = distance - desired`
  - `rel = ego_speed - lead_speed`
  - `ttc = distance/rel if rel > 0 else None`
- **Emergency** (`ttc` is not None and `ttc < threshold`): set `acc = max_decel` (-8.0) and `mode = 'emergency'`.
- **Follow**:
  - Use `acc_d = pid_distance.compute(distance_error, dt)`, optionally plus a speed-matching term such as `k*(lead_speed - ego_speed)`.
  - Use `acc = min(acc_d, pid_speed.compute(set_speed - ego_speed, dt))` so the car never exceeds the set speed.
  - `mode = 'follow'`.
- Always clamp: `acc = max(-8.0, min(acc, 3.0))`.
- Consider resetting the other PID's integral on mode change.

**4. simulation.py**

- Load the config with `yaml.safe_load`.
- Load gains from `tuning_results.yaml` at runtime. No tuning logic is allowed in this file.
- Read `sensor_data.csv` and use only its `lead_speed` and `distance` columns as lead data. Ego speed is simulated from 0.
- Loop over all 1501 rows (t = 0.0 … 150.0, dt = 0.1). At each step:
  - Lead data: `lead = None if isna(row.lead_speed) else row.lead_speed`; distance is the row's distance, or None.
  - Command: `acc, mode, derr = acc.compute(ego, lead, dist, 0.1)`.
  - TTC: `dist/(ego-lead)` if a lead is present and `ego > lead`, else blank.
  - **Record first**, then integrate: `ego = max(0, ego + acc*dt)`.
- The example rows confirm this order: t=0.0 has ego_speed 0.0 and accel 3.0; t=0.1 has 0.3.
- Simple approach: use the sensor `distance` as the measured gap. A valid alternative is to propagate the gap kinematically, `d -= (ego-lead)*dt`, seeded from the sensor value when a lead first appears. Whichever you choose, document it in the report and check that the minimum distance stays > 5 m.
- Output columns, in this exact order: `time,ego_speed,acceleration_cmd,mode,distance_error,distance,ttc`.
  - Use `None` for missing values so they write as empty fields. Cruise rows look like `0.0,0.0,3.0,cruise,,,`.
  - Write with `pd.DataFrame(rows, columns=[...]).to_csv('simulation_results.csv', index=False)`.
  - Exactly 1501 data rows. Round time to 1 decimal: `round(i*0.1,1)`.
- `mode` takes only the values `cruise`, `follow` and `emergency`.

**5. Tuning and tuning_results.yaml**

- Tune in a separate script (e.g. `tune.py`) or by hand, never inside `simulation.py`.
- Manual procedure:
  1. Set Ki = Kd = 0 and raise Kp until the response is fast.
  2. Add a small Ki to remove steady-state error.
  3. Add Kd to cut overshoot.
- Reasonable starting points:
  - Speed: kp≈0.5–2, ki≈0.01–0.1, kd≈0–0.5.
  - Distance: kp≈0.1–0.5, ki≈0–0.05, kd≈0–0.5.
- Required ranges: kp in (0,10), ki in [0,5), kd in [0,5).
- Write the file with `yaml.dump(data, f, default_flow_style=False, sort_keys=False)`:

```yaml
pid_speed:
  kp: 1.0
  ki: 0.05
  kd: 0.1
pid_distance:
  kp: 0.3
  ki: 0.01
  kd: 0.2
```

Values must be plain floats (not numpy types). Cast with `float()`.

**6. Metrics (from the skill; compute them on simulation_results.csv)**

- **Rise time:** `t(v ≥ 0.9·30) − t(v ≥ 0.1·30)` on the initial cruise segment. Target < 10 s. With +3 m/s² saturation, 3→27 m/s takes about 8 s, so avoid early cut-off of acceleration.
- **Overshoot:** `(max(v) − 30)/30·100` over cruise rows. Target < 5%.
- **Speed SS error:** `|30 − mean(last portion of a cruise segment)|`. Target < 0.5.
- **Distance SS error:** `mean |distance_error|` over the settled part of follow segments. Target < 2 m.
- **Minimum distance:** `min(distance)`. Target > 5 m.
- **Duration:** 150 s.

Quick check one-liner:

```python
python3 -c "import pandas as pd;d=pd.read_csv('simulation_results.csv');print(len(d),list(d.columns));print(d['mode'].value_counts());print(d.distance.min(),d.ego_speed.max());c=d[d['mode']=='cruise'];print(c.time[c.ego_speed>=3].min(),c.time[c.ego_speed>=27].min())"
```

If rise time, overshoot or distance error fails, adjust the gains in the yaml and rerun `simulation.py`.

**7. acc_report.md**

Use markdown headings with these sections:
- **System Design:** architecture (sensor → mode selector → speed/distance PID → accel clamp → kinematic model), the three modes, and safety features (TTC emergency braking at -8 m/s², headway 1.5 s + 10 m gap, accel limits, anti-windup).
- **PID Tuning Methodology:** procedure and final gains for both controllers.
- **Simulation Results / Performance Metrics:** a table of rise time, overshoot, speed SS error, distance SS error, min distance and duration, each with its target and pass/fail. Generate the numbers from the CSV; do not invent them.

**Plan (≈10–15 commands):**
1. Run the inspect commands from step 1.
2. Write `pid_controller.py`, `acc_system.py` and `simulation.py` with heredocs.
3. Write `tuning_results.yaml`.
4. Run `python3 simulation.py`.
5. Run the check one-liner and a metrics script. Iterate on the gains only.
6. Write `acc_report.md` from the computed metrics.
7. Verify with `head -3` / `wc -l` (expect 1502 lines including the header) and confirm that `from pid_controller import PIDController` and `from acc_system import AdaptiveCruiseControl` import cleanly.

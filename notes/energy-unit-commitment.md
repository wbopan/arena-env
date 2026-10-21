**Input inspection (cheap).**
- Top-level keys: `python3 -c "import json;d=json.load(open('/root/network.json'));print(list(d))"`.
- Then print one thermal generator and one renewable generator, truncating lists with `str(v)[:200]`.
- Expected schema (pglib-uc / UnitCommitment.jl style), but verify each field by meaning:
  - `time_periods` (T, e.g. 48).
  - `demand[T]` and `reserves[T]`, the system spinning-reserve requirement.
  - `thermal_generators`: a dict name → {`must_run`, `power_output_minimum`, `power_output_maximum`, `ramp_up_limit`, `ramp_down_limit`, `startup_limit`, `shutdown_limit`, `time_up_minimum`, `time_down_minimum`, `unit_on_t0`, `time_up_t0`, `time_down_t0`, `power_output_t0`, `piecewise_production` [{mw, cost}], `startup` [{lag, cost}]}.
  - `renewable_generators`: a dict name → {`power_output_minimum[T]`, `power_output_maximum[T]`}.
- Keep dict order for names.
- Assert every series has length T.
- Do not rescale or drop anything.
- There is no network or contingency model: one system balance per hour.

**Formulation.** Use an above-minimum internal variable `p`; actual MW = `pmin*u + p`. For each thermal g and period t, define binaries `u`, `v` (start) and `w` (stop), and continuous `p` and `r` (reserve) ≥ 0.

1. **Transitions:** `u[t] - u[t-1] = v[t] - w[t]`, with `u[-1] = unit_on_t0`.
2. **Must-run:** if must-run, `u = 1`.
3. **Initial obligations:**
   - If on at t0: force `u[t] = 1` for `t < min(T, max(0, UT - time_up_t0))`.
   - If off at t0: force `u[t] = 0` for `t < min(T, max(0, DT - time_down_t0))`.
4. **Minimum up/down (windows truncated at horizon end, no post-horizon obligation):**
   - `sum_{i=t-UT+1..t, i>=0} v[i] <= u[t]`.
   - `sum_{i=t-DT+1..t, i>=0} w[i] <= 1 - u[t]`.
5. **Capacity and reserve deliverability.** Let `cap = pmax - pmin`, `SU = startup_limit`, `SD = shutdown_limit`.
   - Base row: `p[t] + r[t] <= cap*u[t] - max(0, pmax-SU)*v[t]`.
   - If UT > 1, also subtract `max(0, pmax-SD)*w[t+1]` (for t < T-1) in the same row.
   - If UT == 1, use two separate rows: one with the `v[t]` term and one with the `w[t+1]` term.
6. **Ramping** (above-minimum terms). Set `p0 = power_output_t0 - pmin*unit_on_t0`.
   - Ramp up: `p[t] + r[t] - p[t-1] <= RU`.
   - Ramp down: `p[t-1] - p[t] <= RD`, with `p[-1] = p0`.
7. **Offline zeroes:** `p, r <= cap*u`, which is already implied by the capacity row. If `pmax == pmin`, then p and r are 0.
8. **Demand balance:** `sum_g (pmin_g*u + p) + sum_r ren[r,t] = demand[t]`.
   - Renewable output is a variable bounded by `[min[t], max[t]]`. Curtailment is allowed and its cost is 0.
9. **Spinning reserve:** `sum_g r[g,t] >= reserves[t]`. Only online thermal units count; renewables never do.

**Production cost** (piecewise, total-cost breakpoints).
- Sort the points by mw. The first point is at pmin; its cost `c0` counts as `c0*u[t]`.
- For each segment l, add a variable `seg[g,l,t]` in `[0, (mw_l - mw_{l-1})*u]`, done as rows `seg - width*u <= 0`.
- Slope = `(cost_l - cost_{l-1}) / width`.
- Link: `p = sum_l seg`.
- Convex curves need no extra binaries. If a curve is not convex, add segment-order binaries.

**Startup cost tiers** (lags sorted ascending, S tiers). For each tier s, add a binary `delta[g,s,t]` with `sum_s delta = v[t]`.
- For s < S-1: `delta[s,t] <= sum_{i=lag_s}^{lag_{s+1}-1} w[t-i]`, using only in-horizon indices `t-i >= 0`.
- Pre-horizon stops: if the unit is off at t0, it went offline `time_down_t0` hours before t=0. So the hot tier s is allowed only at those t where `t + time_down_t0` lies in `[lag_s, lag_{s+1})`. Add that as a constant to the right-hand side: set it to 1 when the condition holds.
- Startup cost = `sum_s cost_s * delta`.
- When recomputing, offline duration before a start = hours offline, including `time_down_t0` if never on in-horizon. Pick the largest lag ≤ that duration.
- The objective has only production plus startup cost. Do not invent no-load or shutdown costs.

**Solver.** Use `scipy.optimize.milp` (HiGHS) with a sparse `coo_matrix` built via the add_row/alloc pattern from the skills.
- Set `options={"time_limit": 900, "mip_rel_gap": 1e-3, "disp": False}`.
- If `res.x is None`, debug: check t vs t-1 indexing and initial obligations. Do not report.
- Round binaries only if within 1e-4 of 0/1.
- Status mapping:
  - `res.status == 0` → "optimal".
  - Time limit with an incumbent → "time_limit_feasible".
- `reported_mip_gap = float(res.mip_gap)` if it is available and finite, else null.

**Extraction and validation (before writing).**
- Actual production = `pmin*u + p`. Clip tiny negatives to 0. Offline units get exactly 0 production and 0 reserve.
- Recompute and assert, each with tolerance about 1e-5:
  - start/stop match transitions from `unit_on_t0`;
  - min/max output;
  - must-run;
  - min up/down, including the t0 obligations;
  - ramp up/down, including the t0 obligations;
  - SU/SD limits;
  - balance violation;
  - reserve shortfall;
  - renewable bounds.
- Recompute `objective_cost` from the arrays (piecewise interpolation plus tiered startup cost) and check it matches `res.fun` within about 1e-6 relative.

**Output `/root/report.json`.**
- `case_name`: "unit_commitment_schedule".
- `summary`:
  - `solver_status`, `objective_cost` (recomputed), and `reported_mip_gap`;
  - `time_periods` = T, `num_thermal_generators`, `num_renewable_generators`;
  - `total_startups` = Σv and `total_shutdowns` = Σw;
  - `max_demand_balance_violation_MW` and `max_reserve_shortfall_MW`, both as computed floats (≈0).
- `thermal_generators`: in input order, each with `name` (exact input key) and lists of length T:
  - `commitment` (ints);
  - `production_MW` (actual MW, not above-min);
  - `reserve_MW`;
  - `startup` (ints) and `shutdown` (ints).
- `renewable_generators`: `name` and `production_MW[T]`.
- `hourly_summary`: T entries, with `hour` running 1..T. Each entry has:
  - `demand_MW`;
  - `thermal_generation_MW` (sum of actual thermal production);
  - `renewable_generation_MW`;
  - `reserve_requirement_MW`;
  - `scheduled_spinning_reserve_MW`.
- `constraint_check`: all 11 keys set to "pass", but only after the validation asserts succeed.
- Use plain Python floats and ints (no numpy types) and `json.dump`.

**Plan (about 8 commands).**
1. Inspect the keys and one sample generator.
2. Write `/root/uc.py` covering parse, build, solve, extract, validate and write.
3. Run it with `timeout`.
4. Check the output: `python3 -c` to load the report and print the summary, list lengths, and the first hourly row.
5. If any validation fails, fix the encoding and rerun.

## Reference notes

Use Python’s standard-library `json` and `csv`; this is screening of supplied schedules, not an optimization problem. The prompt’s five checks are the complete specification—do not add startup-ramp or reserve-deliverability constraints.

```python
import json, csv

with open("/root/work/case.json") as f:
    case = json.load(f)
with open("/root/work/candidates.json") as f:
    candidates = json.load(f)["schedules"]

generators = case["thermal_generators"]  # name -> parameters
T = len(case["demand"])
assert len(case["reserves"]) == T
```

Inspect `time_periods` to confirm the horizon convention; preserve the order of `schedules` and treat generator names as opaque keys. `production_MW` is **actual total MW**, not output above minimum. Check that each unit’s commitment and production series has length `T`.

For each candidate, initialize five Boolean results to `True`, then accumulate violations rather than stopping at the first one:

- **Balance, hour `t`:** `abs(sum(p[g][t] for g in generators) - demand[t]) <= 0.01`.
- **Limits:** when `u[g][t] == 0`, `abs(p[g][t]) <= 1e-6`; when online, `Pmin - 1e-6 <= p[g][t] <= Pmax + 1e-6`. Commitment values must be 0 or 1.
- **Spinning reserve:** `sum(Pmax[g] - p[g][t] for g in generators if u[g][t] == 1) >= reserves[t] - 0.01`. Count online units only.
- **Ramping:** compare hour 1 with `unit_on_t0` and `power_output_t0`; thereafter compare adjacent hours. **Only when both statuses are online**, require `current_MW - previous_MW <= ramp_up_limit + 1e-6` and `previous_MW - current_MW <= ramp_down_limit + 1e-6`.
- **Minimum up/down:** compare every status to its predecessor, including t0. A start at zero-based index `t` requires online status throughout `range(t, min(T, t + time_up_minimum))`; a stop similarly requires offline status through `time_down_minimum`. Do not require periods beyond the horizon. Separately, per the prompt, if a unit is on at t0 with `time_up_t0 < time_up_minimum`, require it online **for the entire horizon**; apply the analogous entire-horizon offline rule when `time_down_t0 < time_down_minimum`.

Write with `csv.writer` and the exact requested header. Convert each Boolean to `"pass"` or `"fail"`; `overall` passes iff all five Booleans pass. After running the script, inspect the CSV header and confirm one data row per input candidate in input order.

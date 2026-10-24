## Reference notes

Use Python’s standard-library `json` module; no optimization solver is needed because commitment and production are fixed. Read both files as JSON objects and iterate `case["thermal_generators"].items()` to preserve generator order. Use `case["time_periods"]` as the horizon and check each schedule array has that length. `production_MW` is **actual total MW**, not output above minimum.

For each committed hour, interpolate the **total hourly cost** at actual MW between adjacent `piecewise_production` breakpoints. Sort points by `mw`; do not treat their `cost` values as marginal rates or add a separate minimum-output charge. An offline hour contributes zero production cost.

```python
points = sorted((p["mw"], p["cost"]) for p in curve)
# For adjacent (x0, y0), (x1, y1) bracketing mw:
hourly_cost = y0 + (mw - x0) * (y1 - y0) / (x1 - x0)
```

A startup is `on == 1 and previous_on == 0`, using `unit_on_t0` before hour 1. Track consecutive offline hours **before** each hour: initialize the count to `time_down_t0` if initially off, otherwise zero. Increment it after an offline hour; reset it after an online hour. Thus a startup uses the accumulated count before resetting it. `time_up_t0` does not affect these costs.

Startup tiers need not be ordered. At each startup, choose the largest `lag` not exceeding the prior offline count, falling back to the smallest-lag tier:

```python
tiers = sorted(generator["startup"], key=lambda z: z["lag"])
eligible = [z for z in tiers if z["lag"] <= offline_hours]
startup_charge = (eligible[-1] if eligible else tiers[0])["cost"]
```

Accumulate hourly charges at full precision rather than rounding each hour. Write one entry per generator with startup count, production cost, startup cost, and their sum; then write the corresponding fleet totals. Round reported money values to two decimals and keep displayed sums consistent. Use `json.dump` to write `/root/work/cost_report.json`, then reopen it for a quick check of ordering, fields, and totals.

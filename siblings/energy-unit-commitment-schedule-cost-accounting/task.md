# Unit commitment schedule cost accounting

A fixed day-ahead thermal unit commitment schedule must be priced.

Inputs (in /root/work):

- `case.json`: `time_periods` and `thermal_generators`, a dict keyed by generator name. Each generator has:
  - `power_output_minimum` and `power_output_maximum` (MW).
  - `unit_on_t0`: 1/0 status before hour 1.
  - `time_up_t0` and `time_down_t0`: hours already on/off before hour 1.
  - `startup`: a list of `{lag, cost}` tiers. The list is not necessarily sorted.
  - `piecewise_production`: a list of `{mw, cost}` total-cost breakpoints in $/h, running from Pmin to Pmax.
- `schedule.json`: `generators` -> name -> `commitment` (0/1 per hour) and `production_MW` (actual total MW per hour).

Costing rules:

- **Production cost.** In every hour a unit is committed, its hourly cost is the total-cost curve linearly interpolated at its production. Offline hours cost nothing.
- **When a startup occurs.** A startup happens in hour t when the unit is on in t and was off in the previous hour. For hour 1, use `unit_on_t0` as the previous status.
- **Offline duration.** This is the number of consecutive offline hours immediately before t. If the unit has been off since before the horizon, include `time_down_t0`.
- **Startup cost.** Use the cost of the tier with the largest `lag` <= offline duration. If no tier qualifies, use the smallest-lag tier.
- **Other costs.** There are no other costs.

Output `/root/work/cost_report.json`:

```
{"generators": [{"name": str, "num_startups": int, "production_cost": float,
                 "startup_cost": float, "total_cost": float}, ...],
 "total_production_cost": float, "total_startup_cost": float, "total_cost": float}
```

List generators in input order. A generator's `total_cost` is its production plus startup cost. All money values are in $, rounded to 2 decimals.

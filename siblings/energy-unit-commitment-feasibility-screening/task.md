# Unit commitment schedule feasibility screening

Several candidate day-ahead schedules were proposed for a small thermal system. Screen each one.

Inputs (in /root/work):

- `case.json` contains:
  - `time_periods`.
  - `demand` and `reserves`: MW per hour.
  - `thermal_generators`, keyed by name. Each has `power_output_minimum` and `power_output_maximum` (MW), `ramp_up_limit` and `ramp_down_limit` (MW/h), and `time_up_minimum` and `time_down_minimum` (h).
  - The pre-horizon (t0) state of each generator: `unit_on_t0`, `time_up_t0`, `time_down_t0` and `power_output_t0`.
- `candidates.json` contains `schedules`, a list of `{id, commitment: {name: [0/1,...]}, production_MW: {name: [MW,...]}}`. Production is actual total MW.

A schedule passes a check only if the check holds for every unit and hour:

- `demand_balance`: |sum of production - demand| <= 0.01.
- `generator_limits`: an offline unit produces 0, and an online unit has Pmin <= production <= Pmax.
- `spinning_reserve`: the sum over online units of (Pmax - production) >= reserve - 0.01.
- `ramping`: whenever a unit is online in both the previous and the current hour, the increase must be <= `ramp_up_limit` and the decrease <= `ramp_down_limit`. Hour 1 is compared with the t0 state (`unit_on_t0`, `power_output_t0`).
- `minimum_up_down`:
  - After any status change relative to the previous hour (or t0), the new status must hold for at least the minimum up time (after a start) or the minimum down time (after a stop). This requirement is truncated at the end of the horizon.
  - A unit that is on at t0 with `time_up_t0` < `time_up_minimum` must stay on for the remaining hours.
  - A unit that is off at t0 with `time_down_t0` < `time_down_minimum` must stay off for the remaining hours.

Use a tolerance of 1e-6 wherever none is given.

Write `/root/work/checks.csv` with the header `schedule,demand_balance,generator_limits,spinning_reserve,ramping,minimum_up_down,overall`. Write one row per candidate, in input order:

- `schedule` is the candidate's `id`.
- Each check column is `pass` or `fail`.
- `overall` is `pass` only if all five checks pass.

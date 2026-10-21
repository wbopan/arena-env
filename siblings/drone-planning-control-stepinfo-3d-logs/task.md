# 3D step-response metrics from flight logs

A quadrotor flew several point-to-point maneuvers. The logged positions are in `/root/work/flights.csv`, with columns `flight_id,t,x,y,z`. Time `t` is in seconds and positions are in metres. Rows are not guaranteed to be in time order, so order each flight's samples by `t`. Target positions are in `/root/work/targets.json`, which maps each flight id (a string) to `[x, y, z]`.

For each flight, compute the 3D Euclidean distance `d[k] = ||p[k] - target||` for every sample. Let `d0` be `d` at the earliest sample. The settling threshold is 0.02.

- `RiseTime`: the first `t` where `d <= 0.1*d0`. Use `null` if this is never reached.
- `SettlingTime`: the last `t` where `d > 0.02*d0`. Use 0.0 if there is no such sample.
- `Overshoot_pct`: let `k0` be the first sample where `d <= 0.02*d0`. Take the maximum of `d` over all samples `k >= k0`, divide by `d0`, and multiply by 100. Use 0.0 if the band is never entered.
- `SteadyStateError`: `d` at the last sample, in metres.

If `d0 < 1e-6`, all four metrics are 0.0. Report times as the logged `t` values, with no interpolation.

Write `/root/work/step_metrics.json`. It must be a JSON object keyed by flight id, using the same strings as in targets.json. Each value must be an object with exactly the keys `RiseTime`, `SettlingTime`, `Overshoot_pct`, `SteadyStateError`. Round numbers to 4 decimals.

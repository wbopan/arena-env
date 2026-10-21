# Room thermal identification and IMC PI tuning

A heater step test was run on a room. The log is `/root/work/calibration.csv`. It has the columns `time` (s), `temperature` (degC, noisy sensor) and `heater_power` (%). The heater stays at 0% for an initial flat period. It then steps to a constant power `u` and holds there.

Model the room as a first-order system:

`T(t') = y_ambient + K*u*(1 - exp(-t'/tau))`

Here `t' = time - t0`, where `t0` is the time of the first row with `heater_power > 0`, and `u` is that row's heater_power.

Compute:
1. `y_ambient`: the mean temperature of all rows with `time < t0`. It is held fixed and is not fitted.
2. `K` (degC per %) and `tau` (s): an ordinary unweighted nonlinear least-squares fit of the model to all rows with `time >= t0`. The fit minimises the sum of squared temperature residuals.
3. `r_squared = 1 - SS_res/SS_tot` and `rmse = sqrt(mean(residual^2))`, both computed over the fitted rows.
4. IMC PI tuning with closed-loop time constant `lambda = 0.75*tau`:
   - `Kp = tau/(K*lambda)` (% per degC)
   - `Ki = Kp/tau` (1/s)

Write `/root/work/estimated_params.json` as one JSON object with the numeric keys `K`, `tau`, `y_ambient`, `r_squared`, `rmse`, `lambda`, `Kp` and `Ki`. Round each value to 4 decimal places.

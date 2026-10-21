1. `cat vehicle_params.yaml` and `head`/`wc` `sensor_data.csv`, checking where `lead_speed` is NaN (no lead means cruise mode).
2. Write `PIDController` (with integral clamp) and `AdaptiveCruiseControl.compute` returning `(acc, mode, dist_err)`: desired gap = v·1.5+10, TTC < 3 gives emergency at -8, clamp to [-8, 3].
3. `simulation.py` loads gains from `tuning_results.yaml`, records each row before updating `ego = max(0, ego + acc·0.1)`, and writes exactly 1501 rows with columns `time,ego_speed,acceleration_cmd,mode,distance_error,distance,ttc` (blank fields in cruise).
4. Compute rise time, overshoot, speed/distance SS error and min distance from the CSV, tune the gains in the yaml until all targets pass, then write `acc_report.md` with design, tuning and metrics sections.

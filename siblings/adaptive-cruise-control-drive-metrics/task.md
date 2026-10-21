An adaptive cruise control (ACC) test drive was logged. Compute its performance metrics.

Inputs:
- /root/work/sim_config.yaml contains `acc_settings.set_speed` (m/s), `acc_settings.time_headway` (s), `acc_settings.min_distance` (m) and `simulation.dt` (s).
- /root/work/drive_log.csv has the columns `time,ego_speed,lead_speed,distance`. Speeds are in m/s and distance is in m. `lead_speed` and `distance` are blank while no lead vehicle is detected.

Definitions:
- The **cruise segment** is all rows before the first row where `lead_speed` is present.
- **Lead rows** are all rows where `lead_speed` is present.

Compute the following metrics:
- `rise_time_s`: take the time of the first cruise row with ego_speed >= 0.9*set_speed. Subtract the time of the first cruise row with ego_speed >= 0.1*set_speed.
- `overshoot_pct`: max(0, (max cruise ego_speed - set_speed) / set_speed * 100).
- `speed_ss_error`: |set_speed - mean ego_speed of the last 25 cruise rows|.
- `distance_ss_error`: |mean of (distance - (min_distance + time_headway*ego_speed)) over the last 50 rows of the file|.
- `min_distance_m`: the minimum distance over the lead rows.
- `min_ttc_s`: the minimum time-to-collision, distance / (ego_speed - lead_speed), over lead rows where ego_speed > lead_speed. Use JSON null if there are no such rows.
- `follow_duration_s`: the number of lead rows multiplied by dt.

Output: write /root/work/metrics.json. It must be a single JSON object with exactly these seven keys. Round every numeric value to 3 decimals.

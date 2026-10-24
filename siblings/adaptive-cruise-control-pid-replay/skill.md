## Reference notes

- Read the YAML with `yaml.safe_load` (PyYAML); access nested values with `config['acc']['set_speed']`, `config['gains']['pid_speed']['kp']`, etc. Use the configured `dt`, not differences between logged timestamps.
- The standard-library `csv.DictReader` preserves input row order. Its fields are strings; a blank lead field is `''`. Convert populated numeric fields with `float(...)`. Write with `csv.writer` to control column order and blank cells precisely.

```python
import csv
import yaml

with open('/root/work/acc_config.yaml') as f:
    config = yaml.safe_load(f)

with open('/root/work/sensor_log.csv', newline='') as f:
    rows = list(csv.DictReader(f))
```

**Per-row definitions:** Use logged speeds and distance without updating vehicle dynamics. No lead means `cruise` and a blank distance error and TTC. With a lead:

```python
distance_error = distance - (min_distance + time_headway * ego_speed)
closing_speed = ego_speed - lead_speed
ttc = distance / closing_speed if closing_speed > 0 else None
mode = 'emergency' if ttc is not None and ttc < ttc_threshold else 'follow'
```

Reset **both** PIDs before processing the first row and whenever the mode changes. A reset must make the *next* derivative zero—not compare its error against zero. Only step the speed PID in `cruise` (error `set_speed - ego_speed`), and the distance PID in `follow` (error `distance_error`). In `emergency`, step neither; use `max_decel` as `u`.

```python
# PID state: integral = 0.0; previous_error = None on reset
integral += error * dt
derivative = 0.0 if previous_error is None else (error - previous_error) / dt
u = kp * error + ki * integral + kd * derivative
previous_error = error
```

Do not clamp the PID integral or its internal output: clamp only the final command with `max(max_decel, min(u, max_accel))`.

Write exactly `time,mode,accel_cmd,distance_error,ttc`, one row per input row. Format populated cells with `f'{time:.1f}'`, `f'{accel_cmd:.4f}'`, and `f'{value:.3f}'` for distance error/TTC; use `''` for undefined cells. After running the script, inspect the header, row count, and a few cruise, follow, and emergency rows.

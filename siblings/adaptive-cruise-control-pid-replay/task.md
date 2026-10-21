Replay an adaptive cruise control (ACC) controller, open loop, against a logged drive.

Inputs:
- /root/work/acc_config.yaml contains:
  - `acc`: `set_speed`, `time_headway`, `min_distance`, `ttc_threshold`
  - `limits`: `max_accel`, `max_decel`
  - `dt`
  - `gains`: `pid_speed` and `pid_distance`, each with `kp`, `ki`, `kd`
- /root/work/sensor_log.csv has the columns `time,ego_speed,lead_speed,distance`. The lead fields are blank when no lead vehicle is present.

Use the speeds exactly as logged. Do not integrate any vehicle dynamics.

Process each row in order:
1. If there is no lead, the mode is `cruise`. Otherwise:
   - distance_error = distance - (min_distance + time_headway*ego_speed).
   - If ego_speed > lead_speed, ttc = distance/(ego_speed - lead_speed). Otherwise ttc is undefined.
   - The mode is `emergency` if ttc is defined and ttc < ttc_threshold. Otherwise it is `follow`.
2. On the first row, or when the mode differs from the previous row's mode, reset both PID controllers.
3. Compute u:
   - `cruise`: u = speed PID applied to the error set_speed - ego_speed.
   - `follow`: u = distance PID applied to distance_error.
   - `emergency`: u = max_decel, and no PID is stepped.
4. accel_cmd = clamp(u, max_decel, max_accel).

PID step with error e:
- integral += e*dt
- derivative = (e - previous e)/dt, or 0 on the first step after a reset
- output = kp*e + ki*integral + kd*derivative

There is no anti-windup. Only the active controller is stepped.

Write /root/work/commands.csv:
- Header: `time,mode,accel_cmd,distance_error,ttc`
- One row per input row.
- Format time with 1 decimal, accel_cmd with 4 decimals, and distance_error and ttc with 3 decimals.
- Leave distance_error blank in cruise rows. Leave ttc blank when it is undefined.

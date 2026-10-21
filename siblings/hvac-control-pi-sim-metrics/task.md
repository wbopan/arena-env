# Closed-loop PI simulation of a heated room

`/root/work/params.json` contains these parameters:
- `K` (degC per %) and `tau` (s)
- `T_ambient`, `T0`, `setpoint` and `T_max` (degC)
- `Kp` (% per degC) and `Ki` (1/s)
- `dt` and `duration` (s)
- `settle_band` (degC)

Simulate N = round(duration/dt) steps. Start with T[0] = T0 and integral I = 0. For each k = 0..N-1, let e = setpoint - T[k], then:
- If T[k] >= T_max: apply a safety cutoff. Set u = 0, leave I unchanged and count this step as a cutoff.
- Otherwise (anti-windup):
  - I_c = I + e*dt
  - u_raw = Kp*e + Ki*I_c
  - u = min(100, max(0, u_raw))
  - If 0 <= u_raw <= 100, set I = I_c. Otherwise leave I unchanged.
- Update the room: T[k+1] = T[k] + (dt/tau)*(T_ambient + K*u - T[k]).

This gives temperatures T[0..N] at times t_k = k*dt.

Write `/root/work/metrics.json` with these keys:
- `rise_time`: the first t_k with T[k] >= T0 + 0.9*(setpoint - T0); null if this never happens.
- `settling_time`: the smallest t_k such that |T[j] - setpoint| <= settle_band for all j >= k; null if T[N] is outside the band.
- `overshoot_pct`: max(0, (max(T) - setpoint)/(setpoint - T0))*100.
- `max_temp`: max(T).
- `steady_state_error`: |mean of the last m temperatures - setpoint|, where m = max(1, floor(0.2*(N+1))).
- `mean_heater_power`: the mean of the N applied u values (%).
- `safety_cutoffs`: the integer count of cutoff steps.

Round float values to 3 decimals.

# Preheat ramp and conveyor feasibility check

Inputs in /root/work:

- `handbook.md`: reflow oven process handbook. It defines the preheat region, the ramp-rate limit, oven heated lengths and dwell requirements.
- `mes_log.csv`: one row per run, with columns run_id, board_family, oven_id, conveyor_speed_cm_min.
- `thermocouples.csv`: columns run_id, tc_id, time_s, temp_c. Rows are NOT in time order.

Use the handbook's current values. Ignore superseded revisions.

For each run in mes_log.csv:

1. **Ramp.** For every thermocouple, sort its samples by time. Compute the maximum ramp rate (°C/s) over preheat segments, using the handbook's definition of preheat and of the ramp rate.
   - The run value is the worst case: the largest value across its thermocouples. On ties, take the lexicographically smallest tc_id.
   - `ramp_ok` is true when that value, rounded to 2 decimals, is <= the ramp limit.
   - A run without thermocouple data gets `tc_id` = null, `max_preheat_ramp_c_per_s` = null and `ramp_ok` = false.
2. **Conveyor.** Dwell time (s) = heated_length_cm / speed_cm_min * 60.
   - From the oven's heated length and the dwell limits for the board family, derive `speed_min_cm_min` (from the maximum dwell) and `speed_max_cm_min` (from the minimum dwell).
   - `speed_ok` is true when round(speed_min, 2) <= actual speed <= round(speed_max, 2).

Write `/root/work/output/ramp_conveyor.json` with this structure:

```json
{"ramp_limit_c_per_s": 0.0,
 "runs": [{"run_id": "R01", "tc_id": "TC1", "max_preheat_ramp_c_per_s": 0.0, "ramp_ok": true,
           "speed_min_cm_min": 0.0, "speed_max_cm_min": 0.0, "actual_speed_cm_min": 0.0, "speed_ok": true}]}
```

- Sort `runs` by run_id ascending.
- Round all floats to 2 decimals.
- `ramp_ok` and `speed_ok` are JSON booleans.

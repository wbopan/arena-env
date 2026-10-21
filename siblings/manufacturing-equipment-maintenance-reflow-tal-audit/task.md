# Reflow time-above-liquidus (TAL) audit

Inputs in /root/work:

- `mes_log.csv`: one row per production run, with columns run_id, board_family, alloy, oven_id, conveyor_speed_cm_min.
- `thermocouples.csv`: reflow profile samples, with columns run_id, tc_id, time_s, temp_c. Rows are NOT in time order.
- `spec.yaml`: process specification. For each solder alloy it gives liquidus_c, tal_min_s and tal_max_s.

For every run listed in mes_log.csv:

1. For each thermocouple of the run, compute TAL. TAL is the time the temperature is strictly above the liquidus of the run's alloy.
   - Sort the samples by time.
   - Use linear interpolation between consecutive samples.
   - A segment with both endpoints above liquidus counts entirely.
   - A segment that crosses liquidus counts only its interpolated portion above liquidus.
   - A temperature equal to liquidus is not above.
2. The run's representative sensor is the worst case: the thermocouple with the smallest TAL. On ties, take the lexicographically smallest tc_id.
3. The run is `compliant` if its TAL, rounded to 2 decimals, satisfies tal_min_s <= TAL <= tal_max_s. Otherwise it is `non-compliant`.
4. A run with no thermocouple data is `non-compliant`, with empty tc_id and tal_s fields.

Write `/root/work/output/tal_report.csv` with this exact header:

```
run_id,alloy,liquidus_c,tc_id,tal_s,tal_min_s,tal_max_s,status
```

- Write one row per run, sorted by run_id ascending.
- liquidus_c, tal_min_s and tal_max_s are copied from spec.yaml.
- tal_s is in seconds, rounded to 2 decimals.
- status is `compliant` or `non-compliant`.

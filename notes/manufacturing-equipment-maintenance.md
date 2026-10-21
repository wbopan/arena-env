**Goal:** write five JSON files, /app/output/q01.json … q05.json, from /app/data/{handbook.pdf, mes_log.csv, thermocouples.csv, test_defects.csv}. Every numeric limit, region, window and margin must come from the handbook. Never invent values.

**1. Read the handbook cheaply.**
- Extract text: `pdftotext -layout /app/data/handbook.pdf /tmp/hb.txt`. If that is unavailable, use `python -c "import pypdf;print('\n'.join(p.extract_text() for p in pypdf PdfReader('/app/data/handbook.pdf').pages))" > /tmp/hb.txt` (pdfplumber also works).
- Then grep with context instead of printing the whole file: `grep -n -i -E "preheat|soak|ramp|C/s|liquidus|TAL|wetting|peak|margin|conveyor|dwell|heated length|zone length|time-in-oven|cold spot|worst|representative" /tmp/hb.txt | head -80`.
- Use `sed -n 'A,Bp'` on the relevant line ranges.
- Collect the following into a cfg dict:
  - **Preheat region definition.** It is one of three kinds: a temperature band (tmin–tmax °C), a zone list, or a time window.
  - **Ramp-rate limit** in °C/s.
  - **TAL threshold source.** Usually the liquidus, often the MES column `solder_liquidus_c`. If the MES has no such column, use the handbook's alloy value.
  - **TAL min/max** in seconds.
  - **Peak margin** above liquidus, or an absolute minimum peak.
  - **Conveyor rule:** heated/effective length, zone lengths, and the min dwell or max time-in-oven.
  - **Thermocouple guidance:** which sensor is representative, worst-case or cold-spot.
- If several applicable values exist, implement all of them and use the stricter one. Comment the choice in code.

**2. Inspect the CSVs.**
- Run `head -3` and `wc -l` on each file.
- Run `python -c "import pandas as pd;d=pd.read_csv(...);print(d.dtypes);print(d.nunique())"`.
- Check the MES columns: run_id, board_family, conveyor speed (units?), board length/geometry, liquidus, and possibly zone or recipe fields.
- Check the thermocouple columns: run_id, tc_id, time_s, temp_c, possibly zone_id.
- List MES runs that have no TC rows.
- Check the defects columns and how they join to runs (run_id or board_id), plus their counts and types.

**3. Computation rules (from the skills).**
- Cast IDs to str. Sort TCs with `sort_values(["run_id","tc_id","time_s"], kind="mergesort")`. Skip segments with dt <= 0.
- **Ramp:** s_i = (T_i − T_{i−1})/(t_i − t_{i−1}); max ramp = max s_i inside the preheat region.
  - Temperature band: keep a segment only if BOTH endpoints satisfy tmin ≤ T ≤ tmax.
  - Zone band: filter `zone_id in zones`.
  - Time band: filter t_start ≤ time_s ≤ t_end.
  - Run-level value: take the maximum over TCs; on a tie, the smallest tc_id wins. This is the worst-case sensor unless the handbook names a different representative sensor.
  - A run violates if its max ramp exceeds the limit.
  - If there are no valid segments, emit null.
- **TAL:** time above thr = liquidus, using linear interpolation at crossings.
  - A segment fully above thr adds dt.
  - A crossing segment adds the interpolated part: tcross = t0 + (thr−y0)/(y1−y0)·dt.
  - Run-level value: the coldest (minimum TAL) TC, ties broken by smallest tc_id, unless the handbook says otherwise.
  - Status is "compliant" if min ≤ tal ≤ max, else "non-compliant".
- **Peak:** per TC, peak = max(temp_c). Run value = min over TCs (tie → smallest tc_id). Required = liquidus + margin.
  - A run fails if min_peak < required.
  - A run with no TC data fails, with null tc_id and null peak.
- **Conveyor:**
  - With a max time-in-oven: speed_min = L_eff_cm / t_max_s × 60.
  - With a min dwell: speed_max = L_eff/t_min × 60. Check whether the handbook defines L_eff as heated length or heated length plus board length.
  - Watch units: convert mm or m to cm, and per-second to per-minute.
  - meets = actual ≥ required_min (and ≤ max, if a max exists).
  - If parameters are missing, required = null and meets = false.
- **Q5, best run per board_family:**
  - Quality first: fewer defects (or a defect rate, if board counts exist), plus compliance from Q1–Q4.
  - Efficiency second: higher conveyor speed or throughput.
  - Final tie-break: run_id ascending.
  - Check the handbook for any stated selection criteria and follow them.
  - All other runs in the family go in runner_up_run_ids, sorted.

**4. Output format (exact).**
- **q01.json:** `{"ramp_rate_limit_c_per_s": x, "violating_runs": [...sorted], "max_ramp_by_run": {"R…": {"tc_id": "...", "max_preheat_ramp_c_per_s": x}}}`
- **q02.json:** list of `{"run_id","tc_id","tal_s","required_min_tal_s","required_max_tal_s","status"}`, where status is the string "compliant" or "non-compliant".
- **q03.json:** `{"failing_runs": [...], "min_peak_by_run": {"R…": {"tc_id","peak_temp_c","required_min_peak_c"}}}`
- **q04.json:** list of `{"run_id","required_min_speed_cm_min","actual_speed_cm_min","meets": bool}`
- **q05.json:** list of `{"board_family","best_run_id","runner_up_run_ids":[...]}`
- General rules for all files:
  - Round floats to 2 decimals with `round(float(x),2)`.
  - Never emit NaN or Inf; use null (Python None).
  - Sort lists by run_id or board_family.
  - Emit dict keys sorted.
  - Include all MES runs, using null where there is no data.
  - Convert numpy types to plain Python before `json.dump`.

**5. Plan.**
1. Extract and grep the handbook, then note the cfg values.
2. Check CSV heads and columns.
3. Write a single script `/app/solve.py` containing cfg, the helper functions above, and all five outputs. Run `os.makedirs('/app/output',exist_ok=True)` first.
4. Run it, then `python -c "import json;[print(f,str(json.load(open('/app/output/'+f)))[:300]) for f in ['q01.json','q02.json','q03.json','q04.json','q05.json']]"`.
5. Spot-check one run by hand: check its ramp band, the TAL crossing, and the unit conversions.
6. Confirm there are no NaN values and that sorting is correct.

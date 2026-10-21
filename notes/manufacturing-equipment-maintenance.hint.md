1. Run `pdftotext handbook.pdf` and grep it for preheat/ramp/liquidus/TAL/peak margin/conveyor/heated length/dwell/worst-case to get every limit; also `head` the 3 CSVs.
2. In one pandas script, sort TCs by time and compute: max ramp in the preheat region (both endpoints in band, max over TCs); interpolated TAL above liquidus (coldest TC); min peak vs liquidus+margin (no TC data = fail); min conveyor speed = L_eff/t_max×60.
3. Q5: per family, pick the best run by defects/compliance, then speed, then run_id; the rest are runner-ups.
4. Write /app/output/q01–q05.json in the exact schemas: 2-dp floats, null not NaN, sorted IDs. Then reload and spot-check one run.

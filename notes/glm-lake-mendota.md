**Goal and outputs.** Run GLM from `/root` so that `/root/output/output.nc` covers 2009-01-01 to 2015-12-30. The final calibrated parameters must be saved in `/root/glm3.nml`, and GLM must run successfully with them. Target RMSE against `/root/field_temp_oxy.csv` is below 2.0 °C. The last GLM run you make must use the final nml, so that output.nc and glm3.nml agree.

**Running GLM.**
- Run `cd /root && glm > /tmp/glm.log 2>&1; tail -5 /tmp/glm.log`. Never print the full log.
- GLM reads `glm3.nml` in the current directory and writes `output/output.nc`. Create the directory first with `mkdir -p /root/output`.
- Time a single run, e.g. `time glm >/dev/null`. The run time tells you how many calibration runs you can afford.

**Inspect cheaply first.** Do not cat whole files.
- `cp /root/glm3.nml /root/glm3.nml.bak` (back up before editing).
- `grep -nE "start|stop|timefmt|dt|out_dir|out_fn|nsave|lake_depth|Kw|coef_mix_hyp|wind_factor|lw_factor|\bch\b|_fl|num_inflows|num_outlet" /root/glm3.nml`
- `ls /root/bcs; head -3 /root/bcs/*.csv`. Check that every `*_fl` file named in the nml exists, and that the met file covers the simulation period (`tail -1` of the met file).
- `head -3 /root/field_temp_oxy.csv; wc -l /root/field_temp_oxy.csv` to see the column names (`datetime`, `depth`, `temp`, …) and the datetime format.

**Fix the &time section if needed.**
- With `timefmt = 2`, you need `start = '2009-01-01 00:00:00'` and `stop = '2015-12-30 00:00:00'`.
- In &output you need `out_dir = 'output'` and `out_fn = 'output'`.
- Keep `nsave` as is. Normally `dt=3600` and `nsave=24` give daily output.

**Editing the namelist.**
- Use Python regex on the existing numeric value. Use word boundaries so that `ch` does not match inside other names:
```python
import re
def modify_nml(path, params):
    s = open(path).read()
    for k, v in params.items():
        s, n = re.subn(rf"(\b{k}\s*=\s*)[-\d\.eE+]+", rf"\g<1>{v}", s)
        assert n >= 1, k
    open(path, 'w').write(s)
```
- After editing, verify with `grep -nE "\b(Kw|ch|wind_factor)\b" glm3.nml`.

**Reading the output.**
- Use netCDF4. Check the time units first: `print(nc.variables['time'].units)`. They are hours since the start.
- `z` is the height above the bottom, with shape (t, layers, 1, 1). `temp` has the same shape.
- Masked or fill values are unused layers. Skip them, and also skip values above about 1e30.
- Depth from surface = `lake_depth - z`, where `lake_depth` comes from `&init_profiles`.
- The skill's reference processing works like this:
  - Date = `datetime(2009,1,1,12,0,0) + hours`.
  - Depth = `round(lake_depth - z)`, keeping only 0 ≤ depth ≤ lake_depth.
  - Group by (datetime, depth) and take the mean.
  - For observations: `pd.to_datetime(datetime)`, round depth to int, rename `temp` to `temp_obs`.
  - Inner merge on (datetime, depth), then RMSE = sqrt(mean((sim − obs)²)).
- Print the number of matched rows. If it is 0, the datetime formats differ (e.g. obs at midnight vs sim at 12:00). In that case, also compute a version merged on the normalized date (`dt.normalize()`) to make sure calibration is meaningful.
- A vectorized implementation (loop over times only) is fast enough.

**Calibration parameters.**

| Parameter | Section | Default | Range |
|-----------|---------|---------|-------|
| `Kw` | &light | 0.3 | 0.1–0.5 |
| `coef_mix_hyp` | &mixing | 0.5 | 0.3–0.7 |
| `wind_factor` | &meteorology | 1.0 | 0.7–1.3 |
| `lw_factor` | &meteorology | 1.0 | 0.7–1.3 |
| `ch` | &meteorology | 0.0013 | 0.0005–0.002 |

Use the bias to choose what to adjust:
- Surface too warm: increase `wind_factor`.
- Deep water too warm: increase `Kw`.
- Stratification too weak: decrease `coef_mix_hyp`.
- Overall warm bias: decrease `lw_factor` or `ch`. A cold bias calls for the opposite.

Diagnose by computing the mean of (sim − obs) for depth < 5 m and depth > 15 m.

**Pitfalls.**
- Stay within the ranges above, or GLM may crash.
- After each run, check that output.nc was regenerated and is non-empty.
- Do not run Nelder-Mead with 150 iterations if GLM is slow. Prefer a small budget:
  - First a default run.
  - Then 5–20 runs of one-at-a-time or coarse grid tuning, run inside one Python script that logs a single line per run.
  - Use `scipy minimize(method='Nelder-Mead', options={'maxiter':20})` only if runs are fast.
- Run long loops with `nohup python3 calib.py > /tmp/calib.log 2>&1 &` and poll with `tail -3`.

**Plan.**
1. Back up the nml and inspect it with the grep, head and wc commands above.
2. Fix the time and output settings if needed. Run glm once, timed.
3. Write `/root/eval.py`, which reads lake_depth from the nml, computes the RMSE, n_matched and bias by depth band, and prints one line.
4. If RMSE ≥ 2, write `/root/calib.py`:
   - It loops over parameter sets using `modify_nml`, `subprocess.run(['glm'], cwd='/root', capture_output=True)` and the eval.
   - It tracks the best set.
   - At the end it writes the best params into `/root/glm3.nml` and reruns glm.
5. Final check:
   - `glm` exits with code 0.
   - `/root/output/output.nc` exists.
   - The time range spans to 2015-12-30: the last time value in hours ÷ 24 is about 2554 days.
   - eval.py reports RMSE < 2.
   - grep the nml to confirm the final values are written there.

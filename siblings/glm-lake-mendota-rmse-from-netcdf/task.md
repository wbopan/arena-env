# Lake Mendota: GLM model-observation fit

A General Lake Model run for Lake Mendota has already been completed.

Inputs:
- `/root/work/output/output.nc` (NetCDF-3 classic). It has these variables:
  - `time`: hours since 2009-01-01 12:00:00.
  - `z`: height of each layer above the lake bottom (m), shape time x layer x 1 x 1.
  - `temp`: water temperature (degC), same shape as `z`.
  - Unused layer slots hold the fill value 9.96921e+36 in either variable. Ignore them.
- `/root/work/glm3.nml` (Fortran namelist). The lake depth is `lake_depth` in the `&init_profiles` section.
- `/root/work/field_temp_oxy.csv`, with columns `datetime`, `depth` (m below surface) and `temp` (degC).

Compute the fit between simulation and observations:
1. For every output time, convert each valid layer to depth below surface = lake_depth - z.
2. Keep only layers with 0 <= depth <= lake_depth.
3. Round each depth to the nearest integer metre. Average the simulated temperatures that share the same (datetime, integer depth).
4. Round the observation depths to the nearest integer metre.
5. Inner-join observations and simulation on exact datetime and integer depth.
6. Over all matched pairs, compute:
   - RMSE = sqrt(mean((sim - obs)^2))
   - bias = mean(sim - obs)

Output: write `/root/work/rmse.json` containing exactly one JSON object:

```
{"rmse": <float degC, 4 decimals>, "bias": <float degC, 4 decimals>, "n_matched": <int number of matched pairs>}
```

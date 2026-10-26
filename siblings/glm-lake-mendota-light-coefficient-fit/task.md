# Fit the light extinction coefficient

A short Lake Mendota GLM run and matching field measurements are available. Use them to fit the light extinction coefficient `Kw`; do not run GLM.

Inputs are `/root/work/glm3.nml`, `/root/work/output/output.nc`, `/root/work/bcs/meteo.csv`, and `/root/work/field_temp_oxy.csv`. The namelist gives `lake_depth` and the current `Kw`. NetCDF variable `time` is hours after 2009-01-01 12:00:00; `z` and `temp` have dimensions `(time, layer, 1, 1)`. `z` is height above the bottom, not depth below the surface. The meteorology file has `datetime,shortwave_W_m2`; observations have `datetime,depth_m,temp_C`.

Match observations to simulation layers by timestamp and depth, where simulated depth is `lake_depth - z`. For every match, define `slope = (depth_m - 10) * shortwave_W_m2 / 200`. Fit one coefficient by ordinary least squares without an intercept to `temp_C - simulated_temp_C = (fitted_Kw - current_Kw) * slope`. Use every matched row.

Write exactly one output file, `/root/work/calibrated_glm3.nml`. It must be a copy of the input namelist with only the numeric value of `Kw` changed to the fitted value, rounded to four decimal places. Preserve every other line and parameter.

1. Back up and grep `/root/glm3.nml` (time, output, lake_depth, Kw/coef_mix_hyp/wind_factor/lw_factor/ch), and head `bcs/*.csv` and `field_temp_oxy.csv`. Make sure start/stop are 2009-01-01 to 2015-12-30 with out_dir `output`.
2. Run `cd /root && glm`, then compute RMSE with netCDF4: depth = round(lake_depth − z), sim time = 2009-01-01 12:00 + hours, inner merge with obs on (datetime, depth). Check the matched count.
3. If RMSE ≥ 2, tune the 5 parameters within their ranges using a small regex-edit loop (word-boundary regex), guided by surface and deep bias.
4. Write the best params to `/root/glm3.nml`, rerun glm so `/root/output/output.nc` matches, and confirm RMSE < 2.

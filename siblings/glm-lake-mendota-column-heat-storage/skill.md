## Reference notes

- **Do not run GLM.** Read the existing output. The namelist is Fortran-style (`lake_depth = ...`); extract that numeric value without changing the file.
- The GLM output guide reads NetCDF with `netCDF4.Dataset`:
  ```python
  from netCDF4 import Dataset
  with Dataset(nc_path, "r") as nc:
      hours = nc.variables["time"][:]
      z = nc.variables["z"][:, :, 0, 0]
      temp = nc.variables["temp"][:, :, 0, 0]
  ```
  `z` is **height above the bottom**, not depth below the surface. NetCDF arrays may be masked; omit invalid height/temperature pairs before sorting each timestamp’s layers by height. Keep each temperature paired with its centre height.
- Read `height_m,area_m2` from the CSV and sort by height. `numpy.interp(boundaries, heights, areas)` gives linearly interpolated boundary areas. For sorted centres \(z_i\), boundaries are `0`, adjacent-centre midpoints, and `lake_depth`. Layer volume is `(upper - lower) * (area_at_lower + area_at_upper) / 2`; use the paired centre temperature for that entire volume.
- Convert time with `datetime(2009, 1, 1, 12) + timedelta(hours=float(hour))`; format with `strftime("%Y-%m-%dT%H:%M:%S")`. Compute each heat value and its difference from the **previous unrounded** heat value, then round the JSON numeric fields to three decimal places. The first difference is zero. Use `json.dump` to write an array of objects with only the three requested keys.

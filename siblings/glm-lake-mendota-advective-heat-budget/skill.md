## Reference notes

- This is a boundary-flux calculation; do not run GLM or change `glm3.nml`.
- The namelist is Fortran-style: find `inflow_fl` within `&inflow` and `outflow_fl` within `&outflow` (sections end at `/`). `inflow_fl` contains **two quoted paths** separated by a comma. Resolve each path relative to `/root/work`.
- Read the CSVs by column name. Match records and output temperatures by **calendar date**, not by row position. Write dates in ascending order.

For NetCDF, `scipy.io.netcdf_file` can read **classic NetCDF** files; it does not read NetCDF-4/HDF5 files. Check the file format before relying on it. With a supported file:

```python
from scipy.io import netcdf_file
import numpy as np
from datetime import datetime, timedelta

with netcdf_file("/root/work/output/output.nc", "r", mmap=False) as nc:
    hours = np.array(nc.variables["time"][:], copy=True)
    z = np.array(nc.variables["z"][:], copy=True)
    temp = np.array(nc.variables["temp"][:], copy=True)

base = datetime(2009, 1, 1, 12)
for i, hour in enumerate(hours):
    date = (base + timedelta(hours=float(hour))).date()
    heights = z[i, :, 0, 0]
    temperatures = temp[i, :, 0, 0]
    # Select the temperature at the greatest valid height.
```

GLM `z` is **height above the lake bottom**, not depth below the surface. Select the layer with the greatest valid `z` at each timestamp; do not assume a fixed layer index. Exclude missing or non-finite layer values when selecting it. No lake-depth conversion or profile averaging is needed.

For each date, set `volume_m3 = flow_m3_s * 86400` for each boundary. Sum the two inflow volumes; keep their temperatures separate for heat:

```python
net_heat_MJ = 4.186 * (
    sum(inflow_volume_m3 * inflow_temp_C for each inflow)
    - outflow_volume_m3 * surface_temp_C
)
```

Positive flux is into the lake, with 0 °C as reference. Write only `/root/work/advective_budget.csv` with the specified header and `f"{value:.3f}"` for each numeric field. A short workflow is: inspect the namelist and NetCDF format, read the named inputs, build a date-to-surface-temperature lookup, calculate each date’s row, then check the written header, date coverage, ordering, and formatting.

# Lake Mendota: stratification from GLM output

## Inputs

GLM output for Lake Mendota is in `/root/work/output/output.nc` (NetCDF-3 classic). It contains these variables:

- `time`: hours since the simulation start. The start is given as `start` in the `&time` section of `/root/work/glm3.nml`.
- `NS`: number of active layers at each time.
- `z`: layer height above the lake bottom (m).
- `temp`: water temperature (degC).

`z` and `temp` have shape time x layer x 1 x 1. Layer index 0 is the bottom layer. Only the first NS[t] layer slots at time t are valid. Later slots contain stale garbage. The lake depth is `lake_depth` in the `&init_profiles` section of `glm3.nml`.

## What to compute

For each output time:

1. Convert the valid layers to depth below surface = lake_depth - z, and order them by depth.
2. `surface_temp` is the temperature of the shallowest valid layer. `bottom_temp` is the temperature of the deepest valid layer.
3. Water density (kg/m3) is:
   rho(T) = 1000*(1 - (T+288.9414)/(508929.2*(T+68.12963))*(T-3.9863)^2)
4. `density_diff` = rho(bottom_temp) - rho(surface_temp).
5. `stratified` = 1 if density_diff > 0.1, else 0.
6. When stratified, `thermocline_depth` is the midpoint depth of the adjacent pair of valid layers (in depth order) with the largest |dT/d(depth)|. When not stratified, leave the field empty.

## Output

Write `/root/work/stratification.csv` with this header:

`datetime,surface_temp,bottom_temp,density_diff,stratified,thermocline_depth`

Write one row per output time, in time order. Formatting:

- `datetime` as YYYY-MM-DD HH:MM
- temperatures (degC) to 3 decimals
- `density_diff` (kg/m3) to 4 decimals
- `stratified` as 0/1
- `thermocline_depth` (m) to 2 decimals

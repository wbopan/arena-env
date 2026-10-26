# Lake-column heat storage

Compute the heat stored in a Lake Mendota water column from a short GLM output and a bathymetric table. This calculation uses layer temperatures and lake geometry; it does not require running GLM.

Inputs are `/root/work/glm3.nml`, `/root/work/output/output.nc`, and `/root/work/bcs/hypsography.csv`. The namelist contains `lake_depth` in metres. The CSV has columns `height_m,area_m2`, giving horizontal lake area at heights above the bottom. Its heights include zero and `lake_depth`. Between listed heights, interpolate area linearly.

NetCDF `time` is hours since 2009-01-01 12:00:00. Variables `z` and `temp` have dimensions `(time, layer, 1, 1)`; `z` is layer-centre height above the bottom and `temp` is °C. For each timestamp, sort layers by height. Set interior layer boundaries halfway between adjacent centres, with the bottom boundary at zero and the top boundary at `lake_depth`. Compute each layer's volume as its boundary-height difference times the average interpolated area at those two boundaries. Use its centre temperature for the whole layer.

With 0 °C as reference, heat storage in GJ is `sum(volume_m3 * temp_C * 4.186 / 1000)`. Write exactly `/root/work/heat_storage.json`: a JSON array in time order, with objects containing exactly `datetime`, `heat_GJ`, and `delta_GJ`. Datetimes use `YYYY-MM-DDTHH:MM:SS`. The first delta is zero; later deltas are differences from the preceding unrounded heat value. Round both numeric fields to three decimal places.

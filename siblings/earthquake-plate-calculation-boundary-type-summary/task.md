# Summarise earthquakes by nearest plate-boundary type

You are a seismotectonics analyst. Two input files are in `/root/work`:

- `boundaries.geojson`: a FeatureCollection of `LineString` plate-boundary features in lon/lat degrees. Each has the properties `Name` (e.g. "AQ-DV") and `Type`, which is one of `subduction`, `transform` or `ridge`.
- `earthquakes.csv`: has the columns `id,time,latitude,longitude,depth_km,mag`.

Consider only earthquakes with `mag >= 4.5`. For each one, find the nearest boundary feature and the distance to it.

**Distance convention:** Project coordinates with `x = R*lambda`, `y = R*phi`.

- `lambda` and `phi` are longitude and latitude in radians.
- `R = 6371.0` km.
- No scaling is applied.

The distance to a LineString is the minimum planar Euclidean distance from the projected point to the feature's projected straight segments. The result is in km.

**Association rule:**

- If the nearest boundary is at most 200 km away, the earthquake is associated with that boundary's `Type`.
- Otherwise the earthquake is unassociated.

**Output:** Write `/root/work/boundary_summary.json` with this structure:

```
{"n_events": int, "unassociated_count": int,
 "by_type": {"subduction": {...}, "transform": {...}, "ridge": {...}}}
```

- `n_events` is the number of earthquakes with `mag >= 4.5`.
- Each `by_type` entry has three fields:
  - `count`: the number of associated events of that type.
  - `mean_distance_km`: the mean nearest-boundary distance of those events, rounded to 2 decimals.
  - `max_magnitude`: the largest `mag` among those events.
- All three type keys must be present. If `count` is 0, set the other two fields to null.

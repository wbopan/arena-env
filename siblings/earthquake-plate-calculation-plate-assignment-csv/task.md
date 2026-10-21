# Assign earthquakes to plates and measure distance to the plate edge

You are a geospatial analyst. Two GeoJSON files are in `/root/work`:

- `plates.geojson`: a FeatureCollection of `Polygon` features. Each has one exterior ring in lon/lat degrees (WGS84) and the properties `Code` and `PlateName`. The plates do not overlap.
- `earthquakes.geojson`: a USGS-style FeatureCollection of `Point` features. Geometry coordinates are `[longitude, latitude, depth_km]`. Properties include `id`, `mag`, `place` and `time` (epoch milliseconds).

For every earthquake that lies inside one of the plate polygons:

1. Determine which plate contains it.
2. Compute its distance to that plate's own boundary, which is the polygon's exterior ring.

Ignore earthquakes that lie outside all plates.

**Distance convention:** Project all coordinates with the equidistant cylindrical projection `x = R*lambda`, `y = R*phi`.

- `lambda` and `phi` are longitude and latitude in radians.
- `R = 6371.0` km.
- No standard-parallel scaling is applied.

The distance is the minimum planar Euclidean distance from the projected point to the ring's edges. Each edge is a straight segment between consecutive projected vertices. The result is in kilometres.

**Output:** Write `/root/work/plate_assignment.csv` with exactly this header:

`id,plate_code,distance_km`

- Write one row per contained earthquake.
- `id` is the earthquake's `properties.id`.
- `plate_code` is the containing plate's `Code`.
- Round `distance_km` to 2 decimal places.
- Sort rows by `distance_km` descending. Break ties by `id` ascending.
- Do not include an index column.
